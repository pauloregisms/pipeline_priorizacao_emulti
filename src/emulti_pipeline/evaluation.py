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


def _safe_auc_ovr(prioridade_referencia_codigo: np.ndarray, probability: np.ndarray, n_classes: int) -> float:
    try:
        return float(roc_auc_score(prioridade_referencia_codigo, probability, multi_class="ovr", average="macro", labels=np.arange(n_classes)))
    except ValueError:
        return float("nan")


def _safe_auprc(prioridade_referencia_codigo: np.ndarray, probability: np.ndarray, target_class: int) -> float:
    binary = (prioridade_referencia_codigo == target_class).astype(int)
    if binary.min() == binary.max():
        return float("nan")
    return float(average_precision_score(binary, probability[:, target_class]))


def calibration_metrics(prioridade_referencia_codigo: np.ndarray, probability_highurgent: np.ndarray) -> dict[str, float]:
    """Calcula Brier, log loss e intercepto/inclinação de calibração binária."""
    binary = (prioridade_referencia_codigo >= 2).astype(int)
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


def calculate_classification_metrics(prioridade_referencia_codigo: np.ndarray, prioridade_prevista_codigo: np.ndarray, probability: np.ndarray, labels: list[int] | None = None) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame]:
    """Compila métricas globais, por classe e matriz de confusão."""
    prioridade_referencia_codigo = np.asarray(prioridade_referencia_codigo, dtype=int)
    prioridade_prevista_codigo = np.asarray(prioridade_prevista_codigo, dtype=int)
    n_classes = probability.shape[1]
    if labels is None:
        labels = list(range(n_classes))

    precision, recall, f1, support = precision_recall_fscore_support(prioridade_referencia_codigo, prioridade_prevista_codigo, labels=labels, zero_division=0)
    per_class = pd.DataFrame(
        {
            "class_code": labels,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    )
    matrix = pd.DataFrame(confusion_matrix(prioridade_referencia_codigo, prioridade_prevista_codigo, labels=labels), index=[f"referencia_{label}" for label in labels], columns=[f"prevista_{label}" for label in labels])

    metrics = {
        "f1_macro": float(f1_score(prioridade_referencia_codigo, prioridade_prevista_codigo, labels=labels, average="macro", zero_division=0)),
        "weighted_kappa": float(cohen_kappa_score(prioridade_referencia_codigo, prioridade_prevista_codigo, weights="quadratic")),
        "ordinal_mae": float(mean_absolute_error(prioridade_referencia_codigo, prioridade_prevista_codigo)),
        "auc_roc_ovr_macro": _safe_auc_ovr(prioridade_referencia_codigo, probability, n_classes),
        "auprc_alta": _safe_auprc(prioridade_referencia_codigo, probability, 2),
        "auprc_urgente": _safe_auprc(prioridade_referencia_codigo, probability, 3),
        "recall_alta": float(recall[labels.index(2)]) if 2 in labels else float("nan"),
        "recall_urgente": float(recall[labels.index(3)]) if 3 in labels else float("nan"),
    }
    metrics.update(calibration_metrics(prioridade_referencia_codigo, probability[:, 2] + probability[:, 3]))
    return metrics, per_class, matrix


def bootstrap_metric_intervals(predictions: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    """Obtém IC percentil por bootstrap das previsões de teste/folds externos."""
    rng = np.random.default_rng(seed)
    if predictions.empty:
        return pd.DataFrame()
    values: list[dict[str, Any]] = []
    prioridade_referencia_codigo = predictions["prioridade_referencia_codigo"].to_numpy(dtype=int)
    prioridade_prevista_codigo = predictions["prioridade_prevista_codigo"].to_numpy(dtype=int)
    probabilities = predictions[[f"proba_{i}" for i in range(4)]].to_numpy(dtype=float)
    indices = np.arange(len(predictions))
    for _ in range(n_bootstrap):
        sampled = rng.choice(indices, size=len(indices), replace=True)
        metric, _, _ = calculate_classification_metrics(prioridade_referencia_codigo[sampled], prioridade_prevista_codigo[sampled], probabilities[sampled])
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
