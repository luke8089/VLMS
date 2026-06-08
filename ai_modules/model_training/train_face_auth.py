"""
MindStack VLMS — Face Authentication Model Training
=====================================================
Trains a Siamese-network-based face verification model used by the
exam proctoring pipeline to confirm student identity at exam start
and during periodic identity checks.

Architecture : ResNet-50 backbone → 512-d embedding → cosine similarity
Dataset      : Internal face capture dataset (3 poses × N students)
Output       : ai_modules/exam_proctoring/weights/face_auth_v2.pt
"""

import os
import argparse
import logging
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import transforms, models
from sklearn.metrics import roc_auc_score, accuracy_score

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────── Config ───────────────────────────

DEFAULTS = {
    "data_dir"       : "data/face_dataset",
    "output_dir"     : "ai_modules/exam_proctoring/weights",
    "embedding_dim"  : 512,
    "margin"         : 0.5,          # contrastive loss margin
    "backbone"       : "resnet50",
    "img_size"       : 224,
    "batch_size"     : 64,
    "epochs"         : 40,
    "lr"             : 3e-4,
    "weight_decay"   : 1e-4,
    "warmup_epochs"  : 3,
    "val_split"      : 0.15,
    "seed"           : 42,
    "num_workers"    : 4,
    "fp16"           : True,
    "patience"       : 7,            # early stopping patience
    "save_best_only" : True,
}

# ─────────────────────────── Dataset ──────────────────────────

TRAIN_TRANSFORMS = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
    transforms.RandomGrayscale(p=0.05),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

VAL_TRANSFORMS = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class FacePairDataset(Dataset):
    """
    Loads (anchor, positive/negative, label) triplets from the student
    face capture directory.  Directory structure expected:

        data/face_dataset/
            student_00001/
                front.jpg
                left.jpg
                right.jpg
            student_00002/
                ...
    """

    def __init__(self, root: str, transform=None, pairs_per_id: int = 10):
        self.root = Path(root)
        self.transform = transform
        self.pairs_per_id = pairs_per_id
        self.identities = sorted(
            [d for d in self.root.iterdir() if d.is_dir()]
        )
        self.id_to_imgs = {
            ident: sorted(ident.glob("*.jpg")) + sorted(ident.glob("*.png"))
            for ident in self.identities
        }
        self.pairs = self._build_pairs()

    def _build_pairs(self):
        pairs = []
        ids = list(self.id_to_imgs.keys())
        for ident in ids:
            imgs = self.id_to_imgs[ident]
            if len(imgs) < 2:
                continue
            # Positive pairs (same identity)
            for _ in range(self.pairs_per_id):
                a, b = random.sample(imgs, 2)
                pairs.append((str(a), str(b), 1))
            # Negative pairs (different identity)
            neg_id = random.choice([x for x in ids if x != ident])
            neg_imgs = self.id_to_imgs[neg_id]
            for _ in range(self.pairs_per_id):
                a = random.choice(imgs)
                b = random.choice(neg_imgs)
                pairs.append((str(a), str(b), 0))
        return pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        from PIL import Image
        path_a, path_b, label = self.pairs[idx]
        img_a = Image.open(path_a).convert("RGB")
        img_b = Image.open(path_b).convert("RGB")
        if self.transform:
            img_a = self.transform(img_a)
            img_b = self.transform(img_b)
        return img_a, img_b, torch.tensor(label, dtype=torch.float32)


# ─────────────────────────── Model ────────────────────────────

class FaceEmbeddingNet(nn.Module):
    """
    ResNet-50 backbone with a projection head that produces
    L2-normalised 512-d embeddings.
    """

    def __init__(self, embedding_dim: int = 512, backbone: str = "resnet50"):
        super().__init__()
        if backbone == "resnet50":
            base = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            feat_dim = 2048
        elif backbone == "resnet34":
            base = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
            feat_dim = 512
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")

        self.backbone = nn.Sequential(*list(base.children())[:-1])  # drop FC

        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(feat_dim, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(1024, embedding_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feats = self.backbone(x)
        emb = self.projection(feats)
        return F.normalize(emb, p=2, dim=1)   # L2-normalised


class ContrastiveLoss(nn.Module):
    """
    Pulls same-identity embeddings together and pushes different-identity
    embeddings apart by at least `margin` in cosine space.
    """

    def __init__(self, margin: float = 0.5):
        super().__init__()
        self.margin = margin

    def forward(
        self,
        emb_a: torch.Tensor,
        emb_b: torch.Tensor,
        labels: torch.Tensor,
    ) -> torch.Tensor:
        sim = F.cosine_similarity(emb_a, emb_b)
        pos_loss = labels * (1 - sim).pow(2)
        neg_loss = (1 - labels) * F.relu(sim - self.margin).pow(2)
        return (pos_loss + neg_loss).mean()


# ─────────────────────────── Training loop ────────────────────

def train_one_epoch(model, loader, criterion, optimizer, scaler, device):
    model.train()
    total_loss, n = 0.0, 0
    for img_a, img_b, labels in loader:
        img_a, img_b, labels = img_a.to(device), img_b.to(device), labels.to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            emb_a = model(img_a)
            emb_b = model(img_b)
            loss = criterion(emb_a, emb_b, labels)
        if scaler:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        total_loss += loss.item() * len(labels)
        n += len(labels)
    return total_loss / n


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, n = 0.0, 0
    all_sims, all_labels = [], []
    for img_a, img_b, labels in loader:
        img_a, img_b, labels = img_a.to(device), img_b.to(device), labels.to(device)
        emb_a = model(img_a)
        emb_b = model(img_b)
        loss = criterion(emb_a, emb_b, labels)
        total_loss += loss.item() * len(labels)
        n += len(labels)
        sims = F.cosine_similarity(emb_a, emb_b).cpu().numpy()
        all_sims.extend(sims.tolist())
        all_labels.extend(labels.cpu().numpy().tolist())

    preds = [1 if s > 0.5 else 0 for s in all_sims]
    acc = accuracy_score(all_labels, preds)
    auc = roc_auc_score(all_labels, all_sims)
    return total_loss / n, acc, auc


# ─────────────────────────── Entry point ──────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Train MindStack face auth model")
    for k, v in DEFAULTS.items():
        p.add_argument(f"--{k.replace('_', '-')}", default=v, type=type(v) if not isinstance(v, bool) else lambda x: x.lower() == 'true')
    return p.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Using device: {device}")

    # ── Datasets ──
    full_dataset = FacePairDataset(args.data_dir, transform=TRAIN_TRANSFORMS)
    val_size = int(len(full_dataset) * args.val_split)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    val_ds.dataset.transform = VAL_TRANSFORMS

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.num_workers, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False,
                              num_workers=args.num_workers, pin_memory=True)
    log.info(f"Train pairs: {train_size:,}  |  Val pairs: {val_size:,}")

    # ── Model ──
    model = FaceEmbeddingNet(
        embedding_dim=args.embedding_dim,
        backbone=args.backbone,
    ).to(device)
    criterion = ContrastiveLoss(margin=args.margin)
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs - args.warmup_epochs, eta_min=1e-6)
    scaler    = torch.cuda.amp.GradScaler() if args.fp16 and device.type == "cuda" else None

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    best_auc, patience_counter = 0.0, 0

    # ── Loop ──
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device)
        val_loss, val_acc, val_auc = evaluate(model, val_loader, criterion, device)

        if epoch > args.warmup_epochs:
            scheduler.step()

        elapsed = time.time() - t0
        log.info(
            f"Epoch {epoch:03d}/{args.epochs}  "
            f"train_loss={train_loss:.4f}  val_loss={val_loss:.4f}  "
            f"val_acc={val_acc:.4f}  val_auc={val_auc:.4f}  "
            f"lr={optimizer.param_groups[0]['lr']:.2e}  "
            f"time={elapsed:.1f}s"
        )

        if val_auc > best_auc:
            best_auc = val_auc
            patience_counter = 0
            ckpt_path = Path(args.output_dir) / "face_auth_v2.pt"
            torch.save({
                "epoch"         : epoch,
                "model_state"   : model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "val_auc"       : val_auc,
                "val_acc"       : val_acc,
                "config"        : vars(args),
            }, ckpt_path)
            log.info(f"  ✓ Best model saved  →  {ckpt_path}  (AUC={best_auc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                log.info(f"Early stopping triggered after {epoch} epochs.")
                break

    log.info(f"Training complete.  Best val AUC: {best_auc:.4f}")


if __name__ == "__main__":
    main()
