"""
MindStack VLMS — Essay & Short-Answer Grading Model Training
=============================================================
Fine-tunes a BERT-based regression model to score student essay and
short-answer responses against a marking rubric.  The model learns
semantic similarity, factual coverage, and Bloom's-level alignment
from a labelled dataset of past graded submissions.

Architecture : bert-base-uncased → mean-pool → regression head (0–100)
Dataset      : data/essay_dataset/  (graded_submissions.jsonl)
Output       : ai_modules/assessment_ai/weights/essay_grader_v3.pt
"""

import os
import json
import logging
import argparse
import random
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, SequentialLR
from transformers import BertTokenizerFast, BertModel
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import pearsonr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────── Config ───────────────────────────

@dataclass
class TrainingConfig:
    data_path       : str   = "data/essay_dataset/graded_submissions.jsonl"
    output_dir      : str   = "ai_modules/assessment_ai/weights"
    model_name      : str   = "bert-base-uncased"
    max_length      : int   = 512
    batch_size      : int   = 16
    grad_accum      : int   = 4         # effective batch = 64
    epochs          : int   = 20
    lr              : float = 2e-5
    warmup_ratio    : float = 0.1
    weight_decay    : float = 0.01
    dropout         : float = 0.2
    val_split       : float = 0.2
    seed            : int   = 42
    fp16            : bool  = True
    patience        : int   = 5
    num_workers     : int   = 2
    label_smoothing : float = 0.05     # prevents overconfident scores


# ─────────────────────────── Dataset ──────────────────────────

@dataclass
class EssaySample:
    question_text   : str
    model_answer    : str
    student_answer  : str
    bloom_level     : str       # remember/understand/apply/analyse/evaluate/create
    max_marks       : float
    awarded_marks   : float
    rubric_notes    : Optional[str] = None

    @property
    def normalised_score(self) -> float:
        """Scale award to [0, 1] for regression target."""
        if self.max_marks <= 0:
            return 0.0
        return min(1.0, max(0.0, self.awarded_marks / self.max_marks))


BLOOM_LEVELS = {
    "remember": 0, "understand": 1, "apply": 2,
    "analyse": 3, "evaluate": 4, "create": 5,
}


class EssayGradingDataset(Dataset):
    """
    Each JSONL record:
      {
        "question": "...",
        "model_answer": "...",
        "student_answer": "...",
        "bloom_level": "apply",
        "max_marks": 10,
        "awarded_marks": 7.5,
        "rubric_notes": "..."   (optional)
      }
    """

    def __init__(self, samples: List[EssaySample], tokenizer, max_length: int):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]

        # Encode [CLS] question [SEP] model_answer [SEP] student_answer [SEP]
        enc = self.tokenizer(
            s.question_text + " " + s.model_answer,
            s.student_answer,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        bloom_id = torch.tensor(BLOOM_LEVELS.get(s.bloom_level, 0), dtype=torch.long)
        score    = torch.tensor(s.normalised_score, dtype=torch.float32)

        return {
            "input_ids"      : enc["input_ids"].squeeze(0),
            "attention_mask" : enc["attention_mask"].squeeze(0),
            "token_type_ids" : enc.get("token_type_ids", torch.zeros(self.max_length, dtype=torch.long)).squeeze(0),
            "bloom_level"    : bloom_id,
            "score"          : score,
        }


def load_samples(path: str) -> List[EssaySample]:
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line.strip())
            samples.append(EssaySample(
                question_text  = d.get("question", ""),
                model_answer   = d.get("model_answer", ""),
                student_answer = d.get("student_answer", ""),
                bloom_level    = d.get("bloom_level", "understand"),
                max_marks      = float(d.get("max_marks", 10)),
                awarded_marks  = float(d.get("awarded_marks", 0)),
                rubric_notes   = d.get("rubric_notes"),
            ))
    return samples


# ─────────────────────────── Model ────────────────────────────

class EssayGraderModel(nn.Module):
    """
    BERT encoder with a Bloom-level-conditioned regression head.
    The Bloom embedding is concatenated to the [CLS] token representation
    so the model can calibrate strictness per cognitive level.
    """

    def __init__(self, bert_name: str, dropout: float = 0.2, n_bloom: int = 6):
        super().__init__()
        self.bert = BertModel.from_pretrained(bert_name)
        hidden   = self.bert.config.hidden_size    # 768

        self.bloom_emb = nn.Embedding(n_bloom, 32)

        self.regressor = nn.Sequential(
            nn.Linear(hidden + 32, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(512, 128),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(128, 1),
            nn.Sigmoid(),              # output in [0, 1]
        )

    def forward(self, input_ids, attention_mask, token_type_ids, bloom_level):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )
        # Mean-pool all non-padding tokens for richer representation
        mask_exp = attention_mask.unsqueeze(-1).float()
        pooled   = (outputs.last_hidden_state * mask_exp).sum(1) / mask_exp.sum(1).clamp(min=1e-9)

        bloom_vec = self.bloom_emb(bloom_level)
        combined  = torch.cat([pooled, bloom_vec], dim=-1)
        return self.regressor(combined).squeeze(-1)


# ─────────────────────────── Training loop ────────────────────

class SmoothedMSELoss(nn.Module):
    """MSE with optional label smoothing to avoid score clipping artefacts."""

    def __init__(self, smoothing: float = 0.05):
        super().__init__()
        self.smoothing = smoothing

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        target_s = target * (1 - self.smoothing) + 0.5 * self.smoothing
        return F.mse_loss(pred, target_s)


import torch.nn.functional as F


def train_epoch(model, loader, criterion, optimizer, scaler, accum, device):
    model.train()
    total_loss, n = 0.0, 0
    optimizer.zero_grad()
    for step, batch in enumerate(loader):
        ids  = batch["input_ids"].to(device)
        mask = batch["attention_mask"].to(device)
        tids = batch["token_type_ids"].to(device)
        bloom = batch["bloom_level"].to(device)
        scores = batch["score"].to(device)

        with torch.cuda.amp.autocast(enabled=scaler is not None):
            preds = model(ids, mask, tids, bloom)
            loss  = criterion(preds, scores) / accum

        if scaler:
            scaler.scale(loss).backward()
        else:
            loss.backward()

        if (step + 1) % accum == 0:
            if scaler:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            optimizer.zero_grad()

        total_loss += loss.item() * accum * len(scores)
        n += len(scores)
    return total_loss / n


@torch.no_grad()
def evaluate_epoch(model, loader, device):
    model.eval()
    all_preds, all_targets = [], []
    for batch in loader:
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        tids  = batch["token_type_ids"].to(device)
        bloom = batch["bloom_level"].to(device)
        scores = batch["score"]
        preds  = model(ids, mask, tids, bloom).cpu().numpy()
        all_preds.extend(preds.tolist())
        all_targets.extend(scores.numpy().tolist())

    mae = mean_absolute_error(all_targets, all_preds)
    r2  = r2_score(all_targets, all_preds)
    pcc, _ = pearsonr(all_targets, all_preds)
    return mae, r2, pcc


# ─────────────────────────── Entry point ──────────────────────

def main():
    cfg = TrainingConfig()

    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}")

    samples = load_samples(cfg.data_path)
    log.info(f"Loaded {len(samples):,} graded samples")

    random.shuffle(samples)
    val_n   = int(len(samples) * cfg.val_split)
    val_s   = samples[:val_n]
    train_s = samples[val_n:]

    tokenizer = BertTokenizerFast.from_pretrained(cfg.model_name)
    train_ds = EssayGradingDataset(train_s, tokenizer, cfg.max_length)
    val_ds   = EssayGradingDataset(val_s,   tokenizer, cfg.max_length)
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True,  num_workers=cfg.num_workers)
    val_loader   = DataLoader(val_ds,   batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)
    log.info(f"Train: {len(train_s):,}  |  Val: {len(val_s):,}")

    model     = EssayGraderModel(cfg.model_name, dropout=cfg.dropout).to(device)
    criterion = SmoothedMSELoss(cfg.label_smoothing)
    optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    total_steps  = (len(train_loader) // cfg.grad_accum) * cfg.epochs
    warmup_steps = int(total_steps * cfg.warmup_ratio)
    warmup_sched = LinearLR(optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_steps)
    decay_sched  = LinearLR(optimizer, start_factor=1.0, end_factor=0.0, total_iters=total_steps - warmup_steps)
    scheduler    = SequentialLR(optimizer, schedulers=[warmup_sched, decay_sched], milestones=[warmup_steps])
    scaler       = torch.cuda.amp.GradScaler() if cfg.fp16 and device.type == "cuda" else None

    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    best_mae, patience_count = float("inf"), 0

    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()
        train_loss = train_epoch(model, train_loader, criterion, optimizer, scaler, cfg.grad_accum, device)
        val_mae, val_r2, val_pcc = evaluate_epoch(model, val_loader, device)
        scheduler.step()

        log.info(
            f"Epoch {epoch:02d}/{cfg.epochs}  "
            f"train_loss={train_loss:.5f}  "
            f"val_MAE={val_mae:.4f}  val_R²={val_r2:.4f}  val_PCC={val_pcc:.4f}  "
            f"time={time.time()-t0:.1f}s"
        )

        if val_mae < best_mae:
            best_mae = val_mae
            patience_count = 0
            ckpt = Path(cfg.output_dir) / "essay_grader_v3.pt"
            torch.save({
                "epoch"       : epoch,
                "model_state" : model.state_dict(),
                "val_mae"     : val_mae,
                "val_r2"      : val_r2,
                "val_pcc"     : val_pcc,
                "config"      : cfg.__dict__,
            }, ckpt)
            log.info(f"  ✓ Checkpoint saved  →  {ckpt}  (MAE={best_mae:.4f})")
        else:
            patience_count += 1
            if patience_count >= cfg.patience:
                log.info(f"Early stopping at epoch {epoch}.")
                break

    log.info(f"Done.  Best val MAE: {best_mae:.4f}")


if __name__ == "__main__":
    main()
