"""
MindStack VLMS — Question Difficulty Predictor Training
========================================================
Trains a text-based difficulty regression model that predicts
the Bloom's cognitive level and empirical difficulty (0–1) of a
new exam question, enabling the quiz generator to balance assessment
difficulty automatically.

Architecture : DeBERTa-v3-small → mean-pool → multi-task head
  Task 1 — Bloom level classification  (6 classes)
  Task 2 — Empirical difficulty regression  (0.0 → 1.0)

Dataset  : data/question_dataset/questions.jsonl
Output   : ai_modules/assessment_ai/weights/difficulty_predictor_v2.pt
"""

import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics import (
    accuracy_score, f1_score, mean_absolute_error,
    classification_report,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

BLOOM_LABELS   = ["remember", "understand", "apply", "analyse", "evaluate", "create"]
BLOOM2IDX      = {b: i for i, b in enumerate(BLOOM_LABELS)}

# ─────────────────────────── Config ───────────────────────────

@dataclass
class Config:
    data_path       : str   = "data/question_dataset/questions.jsonl"
    output_dir      : str   = "ai_modules/assessment_ai/weights"
    model_name      : str   = "microsoft/deberta-v3-small"
    max_length      : int   = 256
    batch_size      : int   = 32
    epochs          : int   = 25
    lr              : float = 2e-5
    weight_decay    : float = 0.01
    dropout         : float = 0.1
    val_split       : float = 0.15
    seed            : int   = 42
    fp16            : bool  = True
    patience        : int   = 6
    bloom_loss_wt   : float = 0.6       # weight of classification vs regression loss
    num_workers     : int   = 2

    # Difficulty label noise augmentation
    label_noise_std : float = 0.03      # small noise prevents overfit on human labels


# ─────────────────────────── Dataset ──────────────────────────

@dataclass
class QuestionRecord:
    question_text   : str
    question_type   : str                # mcq / short_answer / essay
    subject_area    : str
    bloom_level     : str
    difficulty      : float              # 0.0 = trivial → 1.0 = very hard
    answer_text     : Optional[str] = None
    options         : Optional[List[str]] = None

    @property
    def bloom_idx(self) -> int:
        return BLOOM2IDX.get(self.bloom_level, 1)


def load_records(path: str) -> List[QuestionRecord]:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line.strip())
            records.append(QuestionRecord(
                question_text = d["question_text"],
                question_type = d.get("question_type", "mcq"),
                subject_area  = d.get("subject_area", "general"),
                bloom_level   = d.get("bloom_level", "understand"),
                difficulty    = float(d.get("difficulty", 0.5)),
                answer_text   = d.get("answer_text"),
                options       = d.get("options"),
            ))
    log.info(f"Loaded {len(records):,} questions")
    return records


class QuestionDataset(Dataset):
    def __init__(
        self,
        records: List[QuestionRecord],
        tokenizer,
        max_length: int,
        label_noise: float = 0.0,
        augment: bool = False,
    ):
        self.records     = records
        self.tokenizer   = tokenizer
        self.max_length  = max_length
        self.label_noise = label_noise
        self.augment     = augment

    def _build_text(self, r: QuestionRecord) -> str:
        parts = [f"[{r.question_type.upper()}]", r.question_text]
        if r.options:
            parts.append("Options: " + " | ".join(r.options[:4]))
        if r.answer_text:
            parts.append("Answer: " + r.answer_text[:200])
        parts.append(f"Subject: {r.subject_area}")
        return " ".join(parts)

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        r = self.records[idx]
        text = self._build_text(r)

        # Simple text augmentation: randomly drop options or truncate
        if self.augment and random.random() < 0.15:
            text = text.split("Options:")[0].strip()

        enc = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        difficulty = r.difficulty
        if self.label_noise > 0:
            difficulty = float(np.clip(
                difficulty + np.random.normal(0, self.label_noise),
                0.0, 1.0,
            ))

        return {
            "input_ids"      : enc["input_ids"].squeeze(0),
            "attention_mask" : enc["attention_mask"].squeeze(0),
            "token_type_ids" : enc.get("token_type_ids",
                                        torch.zeros(self.max_length, dtype=torch.long)).squeeze(0),
            "bloom_label"    : torch.tensor(r.bloom_idx, dtype=torch.long),
            "difficulty"     : torch.tensor(difficulty, dtype=torch.float32),
        }


# ─────────────────────────── Model ────────────────────────────

class DifficultyPredictor(nn.Module):
    """
    Shared DeBERTa encoder with two task heads:
      • Bloom classification (6-way softmax)
      • Difficulty regression (sigmoid → [0, 1])

    The Bloom prediction is fed as an additional signal into the
    difficulty head (curriculum-aware difficulty estimation).
    """

    def __init__(self, model_name: str, n_bloom: int = 6, dropout: float = 0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = self.encoder.config.hidden_size

        self.bloom_head = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, n_bloom),
        )

        self.diff_head = nn.Sequential(
            nn.Linear(hidden + n_bloom, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        kwargs = dict(input_ids=input_ids, attention_mask=attention_mask)
        if token_type_ids is not None:
            kwargs["token_type_ids"] = token_type_ids

        out = self.encoder(**kwargs)

        # Mean pool over non-padding tokens
        mask_f = attention_mask.unsqueeze(-1).float()
        pooled = (out.last_hidden_state * mask_f).sum(1) / mask_f.sum(1).clamp(min=1e-9)

        bloom_logits = self.bloom_head(pooled)
        bloom_soft   = F.softmax(bloom_logits, dim=-1)

        diff_input   = torch.cat([pooled, bloom_soft], dim=-1)
        difficulty   = self.diff_head(diff_input).squeeze(-1)

        return bloom_logits, difficulty


# ─────────────────────────── Loss ─────────────────────────────

class MultiTaskLoss(nn.Module):
    def __init__(self, bloom_weight: float = 0.6):
        super().__init__()
        self.bloom_weight = bloom_weight
        self.ce  = nn.CrossEntropyLoss(label_smoothing=0.1)
        self.mse = nn.MSELoss()

        # Learnable task uncertainty weights (Kendall et al.)
        self.log_sigma_bloom = nn.Parameter(torch.tensor(0.0))
        self.log_sigma_diff  = nn.Parameter(torch.tensor(0.0))

    def forward(self, bloom_logits, bloom_labels, diff_preds, diff_labels):
        loss_bloom = self.ce(bloom_logits, bloom_labels)
        loss_diff  = self.mse(diff_preds, diff_labels)

        sigma_b = torch.exp(self.log_sigma_bloom)
        sigma_d = torch.exp(self.log_sigma_diff)
        combined = (
            loss_bloom / (2 * sigma_b ** 2) + self.log_sigma_bloom +
            loss_diff  / (2 * sigma_d ** 2) + self.log_sigma_diff
        )
        return combined, loss_bloom.item(), loss_diff.item()


# ─────────────────────────── Training loop ────────────────────

def train_epoch(model, loader, criterion, optimizer, scaler, device):
    model.train()
    losses, n = [], 0
    for batch in loader:
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        tids  = batch["token_type_ids"].to(device)
        bl    = batch["bloom_label"].to(device)
        diff  = batch["difficulty"].to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            bloom_logits, diff_preds = model(ids, mask, tids)
            loss, lb, ld = criterion(bloom_logits, bl, diff_preds, diff)
        if scaler:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer); scaler.update()
        else:
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        losses.append(loss.item()); n += len(ids)
    return np.mean(losses)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    all_bloom_pred, all_bloom_true = [], []
    all_diff_pred, all_diff_true   = [], []
    for batch in loader:
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        tids  = batch["token_type_ids"].to(device)
        bl    = batch["bloom_label"].numpy()
        diff  = batch["difficulty"].numpy()
        bloom_logits, diff_preds = model(ids, mask, tids)
        all_bloom_pred.extend(bloom_logits.argmax(-1).cpu().numpy().tolist())
        all_bloom_true.extend(bl.tolist())
        all_diff_pred.extend(diff_preds.cpu().numpy().tolist())
        all_diff_true.extend(diff.tolist())

    bloom_acc = accuracy_score(all_bloom_true, all_bloom_pred)
    bloom_f1  = f1_score(all_bloom_true, all_bloom_pred, average="macro", zero_division=0)
    diff_mae  = mean_absolute_error(all_diff_true, all_diff_pred)
    return bloom_acc, bloom_f1, diff_mae


# ─────────────────────────── Entry point ──────────────────────

def main():
    cfg = Config()
    random.seed(cfg.seed); np.random.seed(cfg.seed); torch.manual_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}  |  Model: {cfg.model_name}")

    records   = load_records(cfg.data_path)
    random.shuffle(records)
    val_n     = int(len(records) * cfg.val_split)
    val_recs  = records[:val_n]
    tr_recs   = records[val_n:]

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    tr_ds  = QuestionDataset(tr_recs,  tokenizer, cfg.max_length, label_noise=cfg.label_noise_std, augment=True)
    val_ds = QuestionDataset(val_recs, tokenizer, cfg.max_length, label_noise=0.0,                 augment=False)
    tr_loader  = DataLoader(tr_ds,  batch_size=cfg.batch_size, shuffle=True,  num_workers=cfg.num_workers)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)
    log.info(f"Train: {len(tr_recs):,}  |  Val: {len(val_recs):,}")

    model    = DifficultyPredictor(cfg.model_name, dropout=cfg.dropout).to(device)
    criterion = MultiTaskLoss(cfg.bloom_loss_wt).to(device)
    optimizer = AdamW(
        [{"params": model.encoder.parameters(), "lr": cfg.lr},
         {"params": model.bloom_head.parameters(), "lr": cfg.lr * 5},
         {"params": model.diff_head.parameters(),  "lr": cfg.lr * 5},
         {"params": criterion.parameters(),         "lr": cfg.lr * 2}],
        weight_decay=cfg.weight_decay,
    )
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2, eta_min=1e-7)
    scaler    = torch.cuda.amp.GradScaler() if cfg.fp16 and device.type == "cuda" else None

    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    best_score, patience_count = -float("inf"), 0

    for epoch in range(1, cfg.epochs + 1):
        t0      = time.time()
        tr_loss = train_epoch(model, tr_loader, criterion, optimizer, scaler, device)
        bloom_acc, bloom_f1, diff_mae = evaluate(model, val_loader, device)
        scheduler.step()

        composite = bloom_f1 * 0.5 + (1 - diff_mae) * 0.5
        log.info(
            f"Epoch {epoch:02d}/{cfg.epochs}  "
            f"train_loss={tr_loss:.4f}  "
            f"bloom_acc={bloom_acc:.4f}  bloom_F1={bloom_f1:.4f}  "
            f"diff_MAE={diff_mae:.4f}  composite={composite:.4f}  "
            f"time={time.time()-t0:.1f}s"
        )

        if composite > best_score:
            best_score = composite; patience_count = 0
            ckpt = Path(cfg.output_dir) / "difficulty_predictor_v2.pt"
            torch.save({
                "epoch"       : epoch,
                "model_state" : model.state_dict(),
                "bloom_acc"   : bloom_acc,
                "bloom_f1"    : bloom_f1,
                "diff_mae"    : diff_mae,
                "config"      : cfg.__dict__,
            }, ckpt)
            log.info(f"  ✓ Best model saved → {ckpt}  (composite={best_score:.4f})")
        else:
            patience_count += 1
            if patience_count >= cfg.patience:
                log.info(f"Early stopping at epoch {epoch}."); break

    log.info(f"Training complete.  Best composite score: {best_score:.4f}")

    # Print final Bloom classification report
    log.info("Generating final classification report on validation set…")
    model.load_state_dict(torch.load(Path(cfg.output_dir) / "difficulty_predictor_v2.pt")["model_state"])
    all_bp, all_bt = [], []
    model.eval()
    with torch.no_grad():
        for batch in val_loader:
            ids  = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            tids = batch["token_type_ids"].to(device)
            bl, _ = model(ids, mask, tids)
            all_bp.extend(bl.argmax(-1).cpu().numpy().tolist())
            all_bt.extend(batch["bloom_label"].numpy().tolist())
    log.info("\n" + classification_report(all_bt, all_bp, target_names=BLOOM_LABELS, zero_division=0))


if __name__ == "__main__":
    main()
