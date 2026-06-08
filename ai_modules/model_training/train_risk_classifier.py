"""
MindStack VLMS — Exam Proctoring Risk Classifier Training
==========================================================
Trains a gradient-boosted ensemble (XGBoost + LightGBM stacked with
a shallow MLP) to predict overall malpractice risk score (0–100) from
a student's behavioural signal sequence during an exam session.

Features used:
  - Tab-switch count & frequency
  - Face-not-detected intervals (seconds)
  - Gaze deviation events
  - Head-pose out-of-bounds count
  - Copy/paste attempts
  - Fullscreen-exit count
  - Phone/book object-detection positive frames
  - Keyboard shortcut violations
  - Window-blur events
  - Periodic face-match confidence (mean, min, std)

Dataset  : data/proctoring_dataset/sessions.csv
Output   : ai_modules/exam_proctoring/weights/risk_classifier_v2.pkl
"""

import argparse
import logging
import pickle
import random
import time
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    mean_absolute_error, r2_score, classification_report,
    confusion_matrix, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb
import lightgbm as lgb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────── Feature schema ───────────────────

FEATURE_COLS = [
    "tab_switch_count",
    "tab_switch_per_min",
    "face_absent_seconds",
    "face_absent_pct",
    "gaze_deviation_events",
    "head_pose_violations",
    "copy_paste_attempts",
    "fullscreen_exit_count",
    "phone_detected_frames",
    "book_detected_frames",
    "keyboard_shortcut_violations",
    "window_blur_events",
    "face_match_mean",
    "face_match_min",
    "face_match_std",
    "exam_duration_minutes",
    "submission_time_pct",     # fraction of allotted time used
]

TARGET_COL    = "risk_score"        # 0–100 continuous
CATEGORY_COL  = "risk_category"     # low / medium / high / critical


# ─────────────────────────── Data loading ─────────────────────

def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    log.info(f"Raw rows: {len(df):,}  |  columns: {list(df.columns)}")

    # Drop sessions with missing core signals
    required = FEATURE_COLS + [TARGET_COL]
    df = df.dropna(subset=required)
    log.info(f"After dropna: {len(df):,} rows")

    # Clip unreasonable values
    df["tab_switch_count"]       = df["tab_switch_count"].clip(0, 200)
    df["face_absent_pct"]        = df["face_absent_pct"].clip(0, 1)
    df["face_match_mean"]        = df["face_match_mean"].clip(0, 1)
    df["face_match_min"]         = df["face_match_min"].clip(0, 1)
    df["face_match_std"]         = df["face_match_std"].clip(0, 1)
    df["risk_score"]             = df["risk_score"].clip(0, 100)

    # Derived features
    df["suspicion_composite"] = (
        df["tab_switch_count"] * 3.0 +
        df["copy_paste_attempts"] * 5.0 +
        df["phone_detected_frames"] * 4.0 +
        df["face_absent_pct"] * 20.0 +
        (1 - df["face_match_mean"]) * 15.0
    )

    # Risk bucket for stratified split
    df[CATEGORY_COL] = pd.cut(
        df[TARGET_COL],
        bins=[-1, 25, 50, 75, 101],
        labels=["low", "medium", "high", "critical"],
    )

    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tab_per_min_sq"]     = df["tab_switch_per_min"] ** 2
    df["face_absent_x_gaze"] = df["face_absent_pct"] * df["gaze_deviation_events"]
    df["match_range"]        = df["face_match_mean"] - df["face_match_min"]
    df["device_total"]       = df["phone_detected_frames"] + df["book_detected_frames"]
    df["behavioural_sum"]    = (
        df["tab_switch_count"] +
        df["copy_paste_attempts"] +
        df["fullscreen_exit_count"] +
        df["keyboard_shortcut_violations"] +
        df["window_blur_events"]
    )
    return df


def prepare_splits(df: pd.DataFrame, val_pct: float = 0.2, seed: int = 42) -> Tuple:
    df = feature_engineering(df)
    all_feats = FEATURE_COLS + [
        "tab_per_min_sq", "face_absent_x_gaze", "match_range",
        "device_total", "behavioural_sum", "suspicion_composite",
    ]

    X = df[all_feats].values.astype(np.float32)
    y = df[TARGET_COL].values.astype(np.float32)
    cats = df[CATEGORY_COL].values

    le = LabelEncoder()
    cats_enc = le.fit_transform(cats)

    # Stratified split on risk category
    from sklearn.model_selection import train_test_split
    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=val_pct, random_state=seed, stratify=cats_enc
    )
    log.info(f"Train: {len(X_tr):,}  |  Val: {len(X_val):,}")
    return X_tr, X_val, y_tr, y_val, all_feats


# ─────────────────────────── Models ───────────────────────────

def build_xgboost(seed: int) -> xgb.XGBRegressor:
    return xgb.XGBRegressor(
        n_estimators        = 800,
        max_depth           = 6,
        learning_rate       = 0.05,
        subsample           = 0.8,
        colsample_bytree    = 0.8,
        reg_alpha           = 0.1,
        reg_lambda          = 1.0,
        min_child_weight    = 3,
        gamma               = 0.1,
        objective           = "reg:squarederror",
        eval_metric         = "mae",
        random_state        = seed,
        n_jobs              = -1,
        verbosity           = 0,
    )


def build_lightgbm(seed: int) -> lgb.LGBMRegressor:
    return lgb.LGBMRegressor(
        n_estimators        = 800,
        max_depth           = 7,
        learning_rate       = 0.05,
        num_leaves          = 63,
        subsample           = 0.8,
        colsample_bytree    = 0.8,
        reg_alpha           = 0.05,
        reg_lambda          = 0.5,
        min_child_samples   = 10,
        random_state        = seed,
        n_jobs              = -1,
        verbose             = -1,
    )


def build_stacking(seed: int) -> StackingRegressor:
    estimators = [
        ("xgb",  build_xgboost(seed)),
        ("lgbm", build_lightgbm(seed)),
        ("gbm",  GradientBoostingRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.08,
            subsample=0.8, random_state=seed,
        )),
        ("rf",   RandomForestRegressor(
            n_estimators=300, max_depth=10, random_state=seed, n_jobs=-1,
        )),
    ]
    final_estimator = Ridge(alpha=1.0)
    return StackingRegressor(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=5,
        n_jobs=-1,
        passthrough=True,
    )


# ─────────────────────────── Training ─────────────────────────

def evaluate_model(model, X_val, y_val):
    preds = model.predict(X_val).clip(0, 100)
    mae   = mean_absolute_error(y_val, preds)
    r2    = r2_score(y_val, preds)
    # Bucket accuracy
    bins  = [0, 25, 50, 75, 101]
    y_cat = np.digitize(y_val, bins)
    p_cat = np.digitize(preds, bins)
    acc   = (y_cat == p_cat).mean()
    return mae, r2, acc, preds


def run_cross_validation(model, X_tr, y_tr, n_splits: int = 5, seed: int = 42):
    log.info(f"Running {n_splits}-fold cross-validation…")
    cats = np.digitize(y_tr, [0, 25, 50, 75, 101])
    skf  = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    cv_mae = []
    for fold, (tr_idx, va_idx) in enumerate(skf.split(X_tr, cats), 1):
        m = pickle.loads(pickle.dumps(model))
        m.fit(X_tr[tr_idx], y_tr[tr_idx])
        preds = m.predict(X_tr[va_idx]).clip(0, 100)
        fold_mae = mean_absolute_error(y_tr[va_idx], preds)
        cv_mae.append(fold_mae)
        log.info(f"  Fold {fold}: MAE={fold_mae:.3f}")
    log.info(f"CV MAE: {np.mean(cv_mae):.3f} ± {np.std(cv_mae):.3f}")
    return cv_mae


def main():
    p = argparse.ArgumentParser(description="Train MindStack risk classifier")
    p.add_argument("--data-path",   default="data/proctoring_dataset/sessions.csv")
    p.add_argument("--output-dir",  default="ai_modules/exam_proctoring/weights")
    p.add_argument("--val-split",   type=float, default=0.2)
    p.add_argument("--seed",        type=int,   default=42)
    p.add_argument("--cv-folds",    type=int,   default=5)
    p.add_argument("--use-stacking", action="store_true",
                   help="Use stacking ensemble (slower but more accurate)")
    args = p.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    df = load_and_clean(args.data_path)
    X_tr, X_val, y_tr, y_val, feat_names = prepare_splits(df, args.val_split, args.seed)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_val_s = scaler.transform(X_val)

    if args.use_stacking:
        log.info("Building stacking ensemble…")
        model = build_stacking(args.seed)
    else:
        log.info("Building XGBoost model…")
        model = build_xgboost(args.seed)

    run_cross_validation(model, X_tr_s, y_tr, n_splits=args.cv_folds, seed=args.seed)

    log.info("Training final model on full training set…")
    t0 = time.time()
    model.fit(X_tr_s, y_tr)
    log.info(f"Training time: {time.time()-t0:.1f}s")

    mae, r2, acc, preds = evaluate_model(model, X_val_s, y_val)
    log.info(
        f"Val results — MAE: {mae:.3f}  |  R²: {r2:.4f}  |  "
        f"Bucket accuracy: {acc:.4f}"
    )

    # Feature importance (XGBoost / LightGBM)
    if hasattr(model, "feature_importances_"):
        imp = sorted(zip(feat_names, model.feature_importances_), key=lambda x: -x[1])
        log.info("Top 10 feature importances:")
        for name, score in imp[:10]:
            log.info(f"  {name:<35} {score:.4f}")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output_dir) / "risk_classifier_v2.pkl"
    with open(out_path, "wb") as f:
        pickle.dump({
            "model"        : model,
            "scaler"       : scaler,
            "feature_cols" : feat_names,
            "val_mae"      : mae,
            "val_r2"       : r2,
            "val_acc"      : acc,
            "seed"         : args.seed,
        }, f)
    log.info(f"Model saved → {out_path}")


if __name__ == "__main__":
    main()
