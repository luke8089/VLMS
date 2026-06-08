"""
MindStack VLMS — Document Summarizer Fine-tuning
=================================================
Fine-tunes a BART-large model on educational document summarisation.
The resulting model condenses uploaded lecture notes, PDFs, and
course materials into concise student-facing summaries.

Architecture : facebook/bart-large-cnn (abstractive summarisation)
Fine-tuning  : LoRA adapters for parameter-efficient training
Dataset      : data/summarizer_dataset/
                 train.jsonl  — {document, summary, subject, doc_type}
                 val.jsonl
Output       : ai_modules/learning_ai/weights/summarizer_v2/
"""

import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    BartTokenizerFast,
    BartForConditionalGeneration,
    get_linear_schedule_with_warmup,
)
from rouge_score import rouge_scorer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────── Config ───────────────────────────

@dataclass
class Config:
    train_path      : str   = "data/summarizer_dataset/train.jsonl"
    val_path        : str   = "data/summarizer_dataset/val.jsonl"
    output_dir      : str   = "ai_modules/learning_ai/weights/summarizer_v2"
    model_name      : str   = "facebook/bart-large-cnn"
    max_input_len   : int   = 1024
    max_target_len  : int   = 256
    batch_size      : int   = 4
    grad_accum      : int   = 8            # effective batch = 32
    epochs          : int   = 5
    lr              : float = 3e-5
    weight_decay    : float = 0.01
    warmup_ratio    : float = 0.06
    fp16            : bool  = True
    seed            : int   = 42
    patience        : int   = 3
    num_workers     : int   = 2

    # Generation params for evaluation
    gen_max_length  : int   = 256
    gen_min_length  : int   = 40
    gen_num_beams   : int   = 4
    gen_length_pen  : float = 2.0
    no_repeat_ngram : int   = 3

    # LoRA settings (applied to encoder/decoder attention)
    use_lora        : bool  = True
    lora_r          : int   = 16
    lora_alpha      : float = 32.0
    lora_dropout    : float = 0.05


# ─────────────────────────── LoRA ─────────────────────────────

class LoRALinear(torch.nn.Module):
    """
    Low-Rank Adaptation layer wrapping an existing nn.Linear.
    Adds rank-r side branch: W' = W + (B @ A) * (alpha / r)
    Only A and B are trained; the original W is frozen.
    """

    def __init__(self, linear: torch.nn.Linear, r: int, alpha: float, dropout: float):
        super().__init__()
        self.linear  = linear
        self.r       = r
        self.scaling = alpha / r
        in_f, out_f  = linear.in_features, linear.out_features

        self.lora_A  = torch.nn.Parameter(torch.randn(r, in_f) * 0.02)
        self.lora_B  = torch.nn.Parameter(torch.zeros(out_f, r))
        self.dropout = torch.nn.Dropout(dropout)

        linear.weight.requires_grad_(False)
        if linear.bias is not None:
            linear.bias.requires_grad_(False)

    def forward(self, x):
        base   = self.linear(x)
        lora   = self.dropout(x) @ self.lora_A.T @ self.lora_B.T
        return base + lora * self.scaling


def apply_lora(model, r: int, alpha: float, dropout: float):
    """Replace q_proj and v_proj in every attention layer with LoRA variants."""
    replaced = 0
    for name, module in model.named_modules():
        if hasattr(module, "q_proj") and isinstance(module.q_proj, torch.nn.Linear):
            module.q_proj = LoRALinear(module.q_proj, r, alpha, dropout)
            replaced += 1
        if hasattr(module, "v_proj") and isinstance(module.v_proj, torch.nn.Linear):
            module.v_proj = LoRALinear(module.v_proj, r, alpha, dropout)
            replaced += 1
    log.info(f"LoRA applied to {replaced} projection layers  (r={r}, α={alpha})")
    return model


def count_trainable(model) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ─────────────────────────── Dataset ──────────────────────────

@dataclass
class SummarisationSample:
    document    : str
    summary     : str
    subject     : str = "general"
    doc_type    : str = "lecture_notes"   # lecture_notes / textbook / slides / paper


def load_jsonl(path: str) -> List[SummarisationSample]:
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line.strip())
            samples.append(SummarisationSample(
                document = d["document"],
                summary  = d["summary"],
                subject  = d.get("subject",  "general"),
                doc_type = d.get("doc_type", "lecture_notes"),
            ))
    return samples


class SummarisationDataset(Dataset):
    DOC_TYPE_PREFIXES = {
        "lecture_notes" : "Summarise the following lecture notes:",
        "textbook"      : "Provide a concise summary of this textbook section:",
        "slides"        : "Summarise the key points from these presentation slides:",
        "paper"         : "Give a brief abstract of this research paper:",
    }

    def __init__(self, samples: List[SummarisationSample], tokenizer, cfg: Config):
        self.samples   = samples
        self.tokenizer = tokenizer
        self.cfg       = cfg

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s   = self.samples[idx]
        prefix = self.DOC_TYPE_PREFIXES.get(s.doc_type, "Summarise:")
        src_text = f"{prefix} {s.document}"

        src = self.tokenizer(
            src_text,
            max_length=self.cfg.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        tgt = self.tokenizer(
            s.summary,
            max_length=self.cfg.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        labels = tgt["input_ids"].squeeze(0).clone()
        labels[labels == self.tokenizer.pad_token_id] = -100   # ignore pad in loss

        return {
            "input_ids"       : src["input_ids"].squeeze(0),
            "attention_mask"  : src["attention_mask"].squeeze(0),
            "labels"          : labels,
        }


# ─────────────────────────── Training ─────────────────────────

def train_epoch(model, loader, optimizer, scheduler, scaler, accum, device):
    model.train()
    total_loss, n = 0.0, 0
    optimizer.zero_grad()
    for step, batch in enumerate(loader):
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        lbl   = batch["labels"].to(device)
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            out  = model(input_ids=ids, attention_mask=mask, labels=lbl)
            loss = out.loss / accum
        if scaler:
            scaler.scale(loss).backward()
        else:
            loss.backward()
        if (step + 1) % accum == 0:
            if scaler:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer); scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        total_loss += loss.item() * accum; n += 1
    return total_loss / n


@torch.no_grad()
def evaluate_rouge(model, loader, tokenizer, cfg, device):
    model.eval()
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    r1, r2, rL, n = 0.0, 0.0, 0.0, 0

    for batch in loader:
        ids  = batch["input_ids"].to(device)
        mask = batch["attention_mask"].to(device)
        lbl  = batch["labels"]

        gen_ids = model.generate(
            input_ids=ids, attention_mask=mask,
            max_length=cfg.gen_max_length,
            min_length=cfg.gen_min_length,
            num_beams=cfg.gen_num_beams,
            length_penalty=cfg.gen_length_pen,
            no_repeat_ngram_size=cfg.no_repeat_ngram,
            early_stopping=True,
        )
        preds   = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
        targets = tokenizer.batch_decode(
            lbl.masked_fill(lbl == -100, tokenizer.pad_token_id),
            skip_special_tokens=True,
        )
        for pred, ref in zip(preds, targets):
            s = scorer.score(ref, pred)
            r1 += s["rouge1"].fmeasure
            r2 += s["rouge2"].fmeasure
            rL += s["rougeL"].fmeasure
            n  += 1

    return r1 / n, r2 / n, rL / n


# ─────────────────────────── Entry point ──────────────────────

def main():
    cfg = Config()
    random.seed(cfg.seed); np.random.seed(cfg.seed); torch.manual_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}  |  Model: {cfg.model_name}")

    tokenizer = BartTokenizerFast.from_pretrained(cfg.model_name)
    model     = BartForConditionalGeneration.from_pretrained(cfg.model_name)

    if cfg.use_lora:
        model = apply_lora(model, r=cfg.lora_r, alpha=cfg.lora_alpha, dropout=cfg.lora_dropout)
        log.info(f"Trainable parameters after LoRA: {count_trainable(model):,}")

    model = model.to(device)

    tr_samples  = load_jsonl(cfg.train_path)
    val_samples = load_jsonl(cfg.val_path)
    log.info(f"Train: {len(tr_samples):,}  |  Val: {len(val_samples):,}")

    tr_ds  = SummarisationDataset(tr_samples,  tokenizer, cfg)
    val_ds = SummarisationDataset(val_samples, tokenizer, cfg)
    tr_loader  = DataLoader(tr_ds,  batch_size=cfg.batch_size, shuffle=True,  num_workers=cfg.num_workers)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)

    optimizer = AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg.lr, weight_decay=cfg.weight_decay,
    )
    total_steps  = (len(tr_loader) // cfg.grad_accum) * cfg.epochs
    warmup_steps = int(total_steps * cfg.warmup_ratio)
    scheduler    = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    scaler       = torch.cuda.amp.GradScaler() if cfg.fp16 and device.type == "cuda" else None

    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    best_rL, patience_count = 0.0, 0

    for epoch in range(1, cfg.epochs + 1):
        t0       = time.time()
        tr_loss  = train_epoch(model, tr_loader, optimizer, scheduler, scaler, cfg.grad_accum, device)
        r1, r2, rL = evaluate_rouge(model, val_loader, tokenizer, cfg, device)

        log.info(
            f"Epoch {epoch}/{cfg.epochs}  "
            f"train_loss={tr_loss:.4f}  "
            f"ROUGE-1={r1:.4f}  ROUGE-2={r2:.4f}  ROUGE-L={rL:.4f}  "
            f"time={time.time()-t0:.1f}s"
        )

        if rL > best_rL:
            best_rL = rL; patience_count = 0
            model.save_pretrained(cfg.output_dir)
            tokenizer.save_pretrained(cfg.output_dir)
            log.info(f"  ✓ Best model saved → {cfg.output_dir}  (ROUGE-L={best_rL:.4f})")
        else:
            patience_count += 1
            if patience_count >= cfg.patience:
                log.info(f"Early stopping at epoch {epoch}."); break

    log.info(f"Done.  Best ROUGE-L: {best_rL:.4f}")


if __name__ == "__main__":
    main()
