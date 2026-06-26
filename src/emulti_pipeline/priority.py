"""Matriz protocolada de prioridade de referência simulada.

Este módulo produz ``prioridade_referencia`` como regra de referência de uma simulação. Não representa
necessidade clínica real nem deve ser utilizado para decisão assistencial.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .utils import sigmoid

PRIORITY_ORDER = ["baixa", "moderada", "alta", "urgente"]
PRIORITY_TO_CODE = {label: index for index, label in enumerate(PRIORITY_ORDER)}


def _required_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Colunas necessárias ausentes para regra de prioridade: {missing}")


def assign_reference_priority(
    profiles: pd.DataFrame,
    psychometrics: pd.DataFrame,
    config: dict[str, Any],
    seed: int,
) -> pd.DataFrame:
    """Aplica a matriz de referência simulada usando dados estruturados, indicadores psicométricos e marcadores de origem.

    A classe urgente segue regras determinísticas de segurança. Para baixa/moderada/alta,
    uma componente probabilística pré-especificada representa incerteza em casos limítrofes.
    """
    merged = profiles.merge(psychometrics, on="patient_id", how="inner", validate="one_to_one")
    required = [
        "phq9_total",
        "gad7_total",
        "idate_estado_total",
        "social_vulnerability",
        "marcadores_origem_ideacao_suicida",
        "marcadores_origem_planejamento_suicida",
        "marcadores_origem_autoagressao_iminente",
        "marcadores_origem_risco_violencia",
        "marcadores_origem_sintomas_psicoticos",
        "marcadores_origem_comprometimento_funcional",
        "marcadores_origem_uso_problematico_substancias",
        "marcadores_origem_agravamento_recente",
        "marcadores_origem_suporte_social_baixo",
    ]
    _required_columns(merged, required)
    rules = config["priority_rules"]
    rng = np.random.default_rng(seed + 3000)

    # Regras de segurança: urgência não é tratada como simples nível ordinal comum.
    urgent = (
        ((merged["marcadores_origem_ideacao_suicida"] == 1) & (merged["marcadores_origem_planejamento_suicida"] == 1))
        | (merged["marcadores_origem_autoagressao_iminente"] == 1)
        | (merged["marcadores_origem_risco_violencia"] == 1)
        | ((merged["marcadores_origem_sintomas_psicoticos"] == 1) & (merged["marcadores_origem_comprometimento_funcional"] >= 3))
    )

    high_evidence = (
        (merged["phq9_total"] >= rules["phq_high"]).astype(int)
        + (merged["gad7_total"] >= rules["gad_high"]).astype(int)
        + (merged["idate_estado_total"] >= rules["stai_high"]).astype(int)
        + (merged["marcadores_origem_comprometimento_funcional"] >= 2).astype(int)
        + merged["marcadores_origem_uso_problematico_substancias"].astype(int)
        + merged["marcadores_origem_agravamento_recente"].astype(int)
        + (merged["social_vulnerability"] >= rules["vulnerability_high"]).astype(int)
        + merged["marcadores_origem_suporte_social_baixo"].astype(int)
    )
    moderate_evidence = (
        (merged["phq9_total"] >= rules["phq_moderate"]).astype(int)
        + (merged["gad7_total"] >= rules["gad_moderate"]).astype(int)
        + (merged["idate_estado_total"] >= rules["stai_moderate"]).astype(int)
        + (merged["marcadores_origem_comprometimento_funcional"] >= 1).astype(int)
        + merged["marcadores_origem_agravamento_recente"].astype(int)
        + merged["marcadores_origem_suporte_social_baixo"].astype(int)
    )

    # Escore latente de decisão somente para baixa/moderada/alta. O ruído representa
    # variabilidade pré-especificada de situações limítrofes, não uma verdade clínica.
    score = 0.85 * high_evidence + 0.35 * moderate_evidence + rng.normal(0, rules["nonurgent_label_noise"], len(merged))
    priority = np.where(score >= 3.0, "alta", np.where(score >= 1.2, "moderada", "baixa"))
    priority = np.where(urgent, "urgente", priority)

    result = pd.DataFrame(
        {
            "patient_id": merged["patient_id"],
            "prioridade_referencia": priority,
            "prioridade_referencia_codigo": [PRIORITY_TO_CODE[label] for label in priority],
            "urgent_rule_triggered": urgent.astype(int),
            "priority_high_evidence": high_evidence.astype(int),
            "priority_moderate_evidence": moderate_evidence.astype(int),
            "priority_rule_seed": seed + 3000,
        }
    )
    return result


def observed_rule_baseline(frame: pd.DataFrame, prefixo_marcadores_extraidos: str = "marcadores_extraidos_") -> np.ndarray:
    """Aplica uma linha de base operacional usando informação observável.

    Esta regra não é treinada. Ela usa os escores e os marcadores extraídos, de modo
    que pode divergir da matriz de referência que recebeu marcadores de origem.
    """
    required = [
        "phq9_total", "gad7_total", "idate_estado_total", "social_vulnerability",
        f"{prefixo_marcadores_extraidos}ideacao_suicida_present",
        f"{prefixo_marcadores_extraidos}planejamento_suicida_present",
        f"{prefixo_marcadores_extraidos}autoagressao_iminente_present",
        f"{prefixo_marcadores_extraidos}risco_violencia_present",
        f"{prefixo_marcadores_extraidos}sintomas_psicoticos_present",
        f"{prefixo_marcadores_extraidos}uso_problematico_substancias_present",
        f"{prefixo_marcadores_extraidos}agravamento_recente_present",
        f"{prefixo_marcadores_extraidos}suporte_social_baixo_present",
        f"{prefixo_marcadores_extraidos}comprometimento_funcional_severity_code",
    ]
    _required_columns(frame, required)

    urgent = (
        ((frame[f"{prefixo_marcadores_extraidos}ideacao_suicida_present"] == 1) & (frame[f"{prefixo_marcadores_extraidos}planejamento_suicida_present"] == 1))
        | (frame[f"{prefixo_marcadores_extraidos}autoagressao_iminente_present"] == 1)
        | (frame[f"{prefixo_marcadores_extraidos}risco_violencia_present"] == 1)
        | ((frame[f"{prefixo_marcadores_extraidos}sintomas_psicoticos_present"] == 1) & (frame[f"{prefixo_marcadores_extraidos}comprometimento_funcional_severity_code"] >= 3))
    )
    high_score = (
        (frame["phq9_total"] >= 20).astype(int)
        + (frame["gad7_total"] >= 15).astype(int)
        + (frame["idate_estado_total"] >= 65).astype(int)
        + (frame[f"{prefixo_marcadores_extraidos}comprometimento_funcional_severity_code"] >= 2).astype(int)
        + frame[f"{prefixo_marcadores_extraidos}uso_problematico_substancias_present"].astype(int)
        + frame[f"{prefixo_marcadores_extraidos}agravamento_recente_present"].astype(int)
        + (frame["social_vulnerability"] >= 0.66).astype(int)
        + frame[f"{prefixo_marcadores_extraidos}suporte_social_baixo_present"].astype(int)
    )
    moderate_score = (
        (frame["phq9_total"] >= 10).astype(int)
        + (frame["gad7_total"] >= 10).astype(int)
        + (frame["idate_estado_total"] >= 50).astype(int)
        + (frame[f"{prefixo_marcadores_extraidos}comprometimento_funcional_severity_code"] >= 1).astype(int)
    )
    result = np.where(high_score >= 3, "alta", np.where(moderate_score >= 2, "moderada", "baixa"))
    return np.where(urgent, "urgente", result)


def rule_baseline_from_available_features(frame: pd.DataFrame) -> np.ndarray:
    """Linha de base que usa somente colunas efetivamente disponíveis no conjunto.

    Serve aos três conjuntos analíticos: dados_estruturados + indicadores_psicometricos, dados_estruturados + indicadores_psicometricos + marcadores_origem e dados_estruturados + indicadores_psicometricos + marcadores_extraidos. Quando um
    marcador não está disponível, assume-se ausência de informação, não ausência clínica.
    """
    def marker(name: str) -> pd.Series:
        if f"marcadores_extraidos_{name}_present" in frame:
            return frame[f"marcadores_extraidos_{name}_present"].fillna(0).astype(int)
        if f"marcadores_origem_{name}" in frame:
            return frame[f"marcadores_origem_{name}"].fillna(0).astype(int)
        return pd.Series(0, index=frame.index, dtype=int)

    if "marcadores_extraidos_comprometimento_funcional_severity_code" in frame:
        functional = frame["marcadores_extraidos_comprometimento_funcional_severity_code"].fillna(0).astype(int)
    elif "marcadores_origem_comprometimento_funcional" in frame:
        functional = frame["marcadores_origem_comprometimento_funcional"].fillna(0).astype(int)
    else:
        functional = pd.Series(0, index=frame.index, dtype=int)

    urgent = (
        ((marker("ideacao_suicida") == 1) & (marker("planejamento_suicida") == 1))
        | (marker("autoagressao_iminente") == 1)
        | (marker("risco_violencia") == 1)
        | ((marker("sintomas_psicoticos") == 1) & (functional >= 3))
    )
    high_score = (
        (frame["phq9_total"].fillna(0) >= 20).astype(int)
        + (frame["gad7_total"].fillna(0) >= 15).astype(int)
        + (frame["idate_estado_total"].fillna(0) >= 65).astype(int)
        + (functional >= 2).astype(int)
        + marker("uso_problematico_substancias")
        + marker("agravamento_recente")
        + (frame["social_vulnerability"].fillna(0) >= 0.66).astype(int)
        + marker("suporte_social_baixo")
    )
    moderate_score = (
        (frame["phq9_total"].fillna(0) >= 10).astype(int)
        + (frame["gad7_total"].fillna(0) >= 10).astype(int)
        + (frame["idate_estado_total"].fillna(0) >= 50).astype(int)
        + (functional >= 1).astype(int)
    )
    result = np.where(high_score >= 3, "alta", np.where(moderate_score >= 2, "moderada", "baixa"))
    return np.where(urgent, "urgente", result)
