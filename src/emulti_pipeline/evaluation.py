"""Métricas de classificação, ordinalidade, calibração e incerteza."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    log_loss,
    mean_absolute_error,
    precision_recall_fscore_support,
    roc_auc_score,
)

from .utils import logit


def _safe_auc_ovr(y_true: np.ndarray, probability: np.ndarray, n_classes: int) -> float:
    try:
        return float(roc_auc_score(y_true, probability, multi_class="ovr", average="macro", labels=np.arange(n_classes)))
    except ValueError:
        return float("nan")


def _safe_auprc(y_true: np.ndarray, probability: np.ndarray, target_class: int) -> float:
    binary = (y_true == target_class).astype(int)
    if binary.min() == binary.max():
        return float("nan")
    return float(average_precision_score(binary, probability[:, target_class]))


def calibration_metrics(y_true: np.ndarray, probability_highurgent: np.ndarray) -> dict[str, float]:
    """Calcula Brier, log loss e intercepto/inclinação de calibração binária."""
    binary = (y_true >= 2).astype(int)
    probability = np.clip(probability_highurgent, 1e-6, 1 - 1e-6)
    brier = float(np.mean((binary - probability) ** 2))
    ll = float(log_loss(binary, np.column_stack([1 - probability, probability]), labels=[0, 1]))
    if binary.min() == binary.max():
        return {"brier_highurgent": brier, "log_loss_highurgent": ll, "calibration_intercept": float("nan"), "calibration_slope": float("nan")}
    calibration_model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    calibration_model.fit(logit(probability).reshape(-1, 1), binary)
    return {
        "brier_highurgent": brier,
        "log_loss_highurgent": ll,
        "calibration_intercept": float(calibration_model.intercept_[0]),
        "calibration_slope": float(calibration_model.coef_[0, 0]),
    }


def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, probability: np.ndarray, labels: list[int] | None = None) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame]:
    """Compila métricas globais, por classe e matriz de confusão."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    n_classes = probability.shape[1]
    if labels is None:
        labels = list(range(n_classes))

    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    per_class = pd.DataFrame(
        {
            "class_code": labels,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    )
    matrix = pd.DataFrame(confusion_matrix(y_true, y_pred, labels=labels), index=[f"true_{label}" for label in labels], columns=[f"pred_{label}" for label in labels])

    metrics = {
        "f1_macro": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "weighted_kappa": float(cohen_kappa_score(y_true, y_pred, weights="quadratic")),
        "ordinal_mae": float(mean_absolute_error(y_true, y_pred)),
        "auc_roc_ovr_macro": _safe_auc_ovr(y_true, probability, n_classes),
        "auprc_alta": _safe_auprc(y_true, probability, 2),
        "auprc_urgente": _safe_auprc(y_true, probability, 3),
        "recall_alta": float(recall[labels.index(2)]) if 2 in labels else float("nan"),
        "recall_urgente": float(recall[labels.index(3)]) if 3 in labels else float("nan"),
    }
    metrics.update(calibration_metrics(y_true, probability[:, 2] + probability[:, 3]))
    return metrics, per_class, matrix


def bootstrap_metric_intervals(predictions: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    """Obtém IC percentil por bootstrap das previsões de teste/folds externos."""
    rng = np.random.default_rng(seed)
    if predictions.empty:
        return pd.DataFrame()
    values: list[dict[str, Any]] = []
    y_true = predictions["y_true"].to_numpy(dtype=int)
    y_pred = predictions["y_pred"].to_numpy(dtype=int)
    probabilities = predictions[[f"proba_{i}" for i in range(4)]].to_numpy(dtype=float)
    indices = np.arange(len(predictions))
    for _ in range(n_bootstrap):
        sampled = rng.choice(indices, size=len(indices), replace=True)
        metric, _, _ = calculate_classification_metrics(y_true[sampled], y_pred[sampled], probabilities[sampled])
        values.append(metric)
    boot = pd.DataFrame(values)
    interval_rows = []
    for column in boot.columns:
        interval_rows.append(
            {
                "metric": column,
                "bootstrap_lower_2_5": float(boot[column].quantile(0.025)),
                "bootstrap_upper_97_5": float(boot[column].quantile(0.975)),
            }
        )
    return pd.DataFrame(interval_rows)
