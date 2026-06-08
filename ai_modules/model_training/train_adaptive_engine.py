"""
MindStack VLMS — Adaptive Learning Engine Training
====================================================
Trains a collaborative-filtering + content-based hybrid model that
predicts the next best learning material for each student based on
their reading history, quiz performance, Bloom's level gaps, and
peer similarity.

Components trained:
  1. Student & material embedding matrix   (matrix factorisation)
  2. Performance-gap MLP                   (predicts weak Bloom levels)
  3. Sequential LSTM                       (next-material recommendation)

Dataset : data/learning_dataset/
            interactions.csv     — (student_id, material_id, progress, score, time_spent)
            materials.csv        — (material_id, course_id, bloom_level, topic, word_count)
            students.csv         — (student_id, department, enrollment_count, avg_score)
Output  : ai_modules/learning_ai/weights/adaptive_engine_v2.pt
"""

import logging
import random
import time
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

BLOOM_LEVELS = ["remember", "understand", "apply", "analyse", "evaluate", "create"]

# ─────────────────────────── Config ───────────────────────────

class Config:
    # Paths
    data_dir         = "data/learning_dataset"
    output_dir       = "ai_modules/learning_ai/weights"

    # Embedding model
    emb_dim          = 64
    mlp_hidden       = [256, 128, 64]
    dropout          = 0.25

    # LSTM
    lstm_hidden      = 128
    lstm_layers      = 2
    lstm_seq_len     = 20          # look-back window of recent materials

    # Training
    batch_size       = 512
    epochs           = 50
    lr               = 1e-3
    weight_decay     = 1e-4
    val_split        = 0.15
    seed             = 42
    patience         = 8
    num_workers      = 2
    neg_sample_ratio = 4           # negative samples per positive for MF


# ─────────────────────────── Data ─────────────────────────────

def load_data(cfg: Config):
    interactions = pd.read_csv(f"{cfg.data_dir}/interactions.csv")
    materials    = pd.read_csv(f"{cfg.data_dir}/materials.csv")
    students     = pd.read_csv(f"{cfg.data_dir}/students.csv")
    return interactions, materials, students


def build_id_maps(interactions):
    student_ids  = sorted(interactions["student_id"].unique())
    material_ids = sorted(interactions["material_id"].unique())
    stu2idx  = {s: i for i, s in enumerate(student_ids)}
    mat2idx  = {m: i for i, m in enumerate(material_ids)}
    return stu2idx, mat2idx, len(student_ids), len(material_ids)


# ── Matrix factorisation dataset ──

class MFDataset(Dataset):
    """
    Positive interactions + sampled negatives for BPR-style training.
    Each sample: (student_idx, material_idx, label, score_normalised)
    """

    def __init__(self, df, stu2idx, mat2idx, n_materials, neg_ratio=4):
        self.samples = []
        all_mats = set(mat2idx.values())
        for _, row in df.iterrows():
            s = stu2idx[row["student_id"]]
            m = mat2idx[row["material_id"]]
            score = float(row.get("score", 0.5))
            self.samples.append((s, m, 1.0, score))
            seen = {m}
            for _ in range(neg_ratio):
                neg = random.choice(list(all_mats - seen))
                self.samples.append((s, neg, 0.0, 0.0))
                seen.add(neg)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s, m, label, score = self.samples[idx]
        return (
            torch.tensor(s, dtype=torch.long),
            torch.tensor(m, dtype=torch.long),
            torch.tensor(label, dtype=torch.float32),
            torch.tensor(score, dtype=torch.float32),
        )


# ── Sequential recommendation dataset ──

class SeqDataset(Dataset):
    """
    For each student: sliding windows of length `seq_len` over their
    interaction history, predicting the next material.
    """

    def __init__(self, df, stu2idx, mat2idx, seq_len=20):
        self.samples = []
        self.seq_len = seq_len
        for stu_id, grp in df.sort_values("created_at").groupby("student_id"):
            mats = [mat2idx[m] for m in grp["material_id"] if m in mat2idx]
            if len(mats) < 2:
                continue
            for i in range(1, len(mats)):
                seq   = mats[max(0, i - seq_len):i]
                pad   = seq_len - len(seq)
                seq   = [0] * pad + seq           # 0 = padding index
                target = mats[i]
                self.samples.append((seq, target, stu2idx[stu_id]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        seq, target, stu = self.samples[idx]
        return (
            torch.tensor(seq,    dtype=torch.long),
            torch.tensor(target, dtype=torch.long),
            torch.tensor(stu,    dtype=torch.long),
        )


# ─────────────────────────── Models ───────────────────────────

class NeuralMF(nn.Module):
    """
    Neural Matrix Factorisation: GMF path + MLP path → concat → sigmoid.
    Also predicts per-interaction score alongside the interaction probability.
    """

    def __init__(self, n_students, n_materials, emb_dim, mlp_hidden, dropout):
        super().__init__()
        # GMF
        self.stu_emb_gmf = nn.Embedding(n_students  + 1, emb_dim, padding_idx=0)
        self.mat_emb_gmf = nn.Embedding(n_materials + 1, emb_dim, padding_idx=0)
        # MLP
        self.stu_emb_mlp = nn.Embedding(n_students  + 1, emb_dim, padding_idx=0)
        self.mat_emb_mlp = nn.Embedding(n_materials + 1, emb_dim, padding_idx=0)

        layers = []
        in_dim = emb_dim * 2
        for h in mlp_hidden:
            layers += [nn.Linear(in_dim, h), nn.ReLU(), nn.Dropout(dropout)]
            in_dim = h
        self.mlp = nn.Sequential(*layers)

        self.final    = nn.Linear(emb_dim + mlp_hidden[-1], 1)
        self.score_hd = nn.Linear(emb_dim + mlp_hidden[-1], 1)

        nn.init.normal_(self.stu_emb_gmf.weight, std=0.01)
        nn.init.normal_(self.mat_emb_gmf.weight, std=0.01)
        nn.init.normal_(self.stu_emb_mlp.weight, std=0.01)
        nn.init.normal_(self.mat_emb_mlp.weight, std=0.01)

    def forward(self, stu, mat):
        gmf = self.stu_emb_gmf(stu) * self.mat_emb_gmf(mat)
        mlp_in = torch.cat([self.stu_emb_mlp(stu), self.mat_emb_mlp(mat)], dim=-1)
        mlp_out = self.mlp(mlp_in)
        combined = torch.cat([gmf, mlp_out], dim=-1)
        interaction = torch.sigmoid(self.final(combined)).squeeze(-1)
        score_pred  = torch.sigmoid(self.score_hd(combined)).squeeze(-1)
        return interaction, score_pred


class NextMaterialLSTM(nn.Module):
    """
    Sequence-to-next-item model: LSTM over material embedding history,
    combined with a student embedding for personalisation.
    """

    def __init__(self, n_students, n_materials, emb_dim, lstm_hidden, lstm_layers, dropout):
        super().__init__()
        self.mat_emb  = nn.Embedding(n_materials + 1, emb_dim, padding_idx=0)
        self.stu_emb  = nn.Embedding(n_students  + 1, emb_dim, padding_idx=0)
        self.lstm     = nn.LSTM(
            input_size=emb_dim, hidden_size=lstm_hidden,
            num_layers=lstm_layers, batch_first=True, dropout=dropout,
        )
        self.dropout  = nn.Dropout(dropout)
        self.proj     = nn.Linear(lstm_hidden + emb_dim, n_materials + 1)

    def forward(self, seq, stu):
        emb = self.mat_emb(seq)                          # (B, T, D)
        out, _ = self.lstm(emb)
        last   = self.dropout(out[:, -1, :])             # last timestep
        s_emb  = self.stu_emb(stu)
        logits = self.proj(torch.cat([last, s_emb], dim=-1))
        return logits


class BloomGapPredictor(nn.Module):
    """
    MLP that predicts which Bloom's levels a student is weakest in,
    given their historical performance vector across 6 levels.
    """

    def __init__(self, dropout: float = 0.25):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6 * 3, 128),   # 6 levels × (avg_score, attempt_count, pass_rate)
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 6),        # weakness score per level
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


# ─────────────────────────── Training ─────────────────────────

def train_mf_epoch(model, loader, optimizer, scaler, device):
    model.train()
    total_loss, n = 0.0, 0
    bce = nn.BCELoss()
    mse = nn.MSELoss()
    for stu, mat, labels, scores in loader:
        stu, mat, labels, scores = stu.to(device), mat.to(device), labels.to(device), scores.to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            inter, score_pred = model(stu, mat)
            loss = bce(inter, labels) + 0.3 * mse(score_pred * labels, scores * labels)
        if scaler:
            scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()
        else:
            loss.backward(); optimizer.step()
        total_loss += loss.item() * len(labels); n += len(labels)
    return total_loss / n


def train_lstm_epoch(model, loader, optimizer, scaler, device):
    model.train()
    total_loss, n = 0.0, 0
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    for seq, target, stu in loader:
        seq, target, stu = seq.to(device), target.to(device), stu.to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            logits = model(seq, stu)
            loss   = criterion(logits, target)
        if scaler:
            scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()
        else:
            loss.backward(); optimizer.step()
        total_loss += loss.item() * len(target); n += len(target)
    return total_loss / n


@torch.no_grad()
def eval_lstm_hit_rate(model, loader, k_vals=(1, 5, 10), device="cpu"):
    model.eval()
    hits = {k: 0 for k in k_vals}
    n = 0
    for seq, target, stu in loader:
        seq, target, stu = seq.to(device), target.to(device), stu.to(device)
        logits = model(seq, stu)
        for k in k_vals:
            top_k  = logits.topk(k, dim=-1).indices
            hit    = (top_k == target.unsqueeze(-1)).any(dim=-1).sum().item()
            hits[k] += hit
        n += len(target)
    return {k: hits[k] / n for k in k_vals}


# ─────────────────────────── Entry point ──────────────────────

def main():
    cfg = Config()
    random.seed(cfg.seed); np.random.seed(cfg.seed); torch.manual_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}")

    interactions, materials, students = load_data(cfg)
    stu2idx, mat2idx, n_stu, n_mat = build_id_maps(interactions)
    log.info(f"Students: {n_stu:,}  |  Materials: {n_mat:,}  |  Interactions: {len(interactions):,}")

    # ── Train/val split ──
    val_n  = int(len(interactions) * cfg.val_split)
    val_df = interactions.sample(val_n, random_state=cfg.seed)
    tr_df  = interactions.drop(val_df.index)

    # ── MF training ──
    log.info("=== Phase 1: Neural Matrix Factorisation ===")
    mf_tr = MFDataset(tr_df,  stu2idx, mat2idx, n_mat, cfg.neg_sample_ratio)
    mf_va = MFDataset(val_df, stu2idx, mat2idx, n_mat, 1)
    mf_tr_loader = DataLoader(mf_tr, batch_size=cfg.batch_size, shuffle=True,  num_workers=cfg.num_workers)
    mf_va_loader = DataLoader(mf_va, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)

    mf_model  = NeuralMF(n_stu, n_mat, cfg.emb_dim, cfg.mlp_hidden, cfg.dropout).to(device)
    mf_optim  = AdamW(mf_model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    mf_sched  = ReduceLROnPlateau(mf_optim, patience=3, factor=0.5, verbose=True)
    mf_scaler = torch.cuda.amp.GradScaler() if device.type == "cuda" else None

    best_mf_loss, mf_patience = float("inf"), 0
    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()
        tr_loss = train_mf_epoch(mf_model, mf_tr_loader, mf_optim, mf_scaler, device)
        mf_sched.step(tr_loss)
        log.info(f"MF  Epoch {epoch:02d}/{cfg.epochs}  train_loss={tr_loss:.5f}  time={time.time()-t0:.1f}s")
        if tr_loss < best_mf_loss:
            best_mf_loss = tr_loss
            mf_patience  = 0
        else:
            mf_patience += 1
            if mf_patience >= cfg.patience:
                log.info("MF early stopping."); break

    # ── LSTM training ──
    log.info("=== Phase 2: Sequential LSTM Recommender ===")
    seq_tr = SeqDataset(tr_df,  stu2idx, mat2idx, cfg.lstm_seq_len)
    seq_va = SeqDataset(val_df, stu2idx, mat2idx, cfg.lstm_seq_len)
    seq_tr_loader = DataLoader(seq_tr, batch_size=cfg.batch_size, shuffle=True,  num_workers=cfg.num_workers)
    seq_va_loader = DataLoader(seq_va, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)

    lstm_model  = NextMaterialLSTM(n_stu, n_mat, cfg.emb_dim, cfg.lstm_hidden, cfg.lstm_layers, cfg.dropout).to(device)
    lstm_optim  = AdamW(lstm_model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    lstm_scaler = torch.cuda.amp.GradScaler() if device.type == "cuda" else None
    best_lstm_loss, lstm_patience = float("inf"), 0

    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()
        tr_loss = train_lstm_epoch(lstm_model, seq_tr_loader, lstm_optim, lstm_scaler, device)
        hits    = eval_lstm_hit_rate(lstm_model, seq_va_loader, k_vals=(1, 5, 10), device=device)
        log.info(
            f"LSTM Epoch {epoch:02d}/{cfg.epochs}  "
            f"train_loss={tr_loss:.5f}  "
            f"Hit@1={hits[1]:.4f}  Hit@5={hits[5]:.4f}  Hit@10={hits[10]:.4f}  "
            f"time={time.time()-t0:.1f}s"
        )
        if tr_loss < best_lstm_loss:
            best_lstm_loss = tr_loss; lstm_patience = 0
        else:
            lstm_patience += 1
            if lstm_patience >= cfg.patience:
                log.info("LSTM early stopping."); break

    # ── Save ──
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(cfg.output_dir) / "adaptive_engine_v2.pt"
    torch.save({
        "mf_state"    : mf_model.state_dict(),
        "lstm_state"  : lstm_model.state_dict(),
        "stu2idx"     : stu2idx,
        "mat2idx"     : mat2idx,
        "n_students"  : n_stu,
        "n_materials" : n_mat,
        "config"      : cfg.__dict__,
    }, out_path)
    log.info(f"Saved adaptive engine → {out_path}")


if __name__ == "__main__":
    main()
