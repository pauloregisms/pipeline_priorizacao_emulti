"""Linha de base independente para extração de marcadores clínicos.

O extrator é deliberadamente baseado em regras/dicionário, para não depender do mesmo
mecanismo usado na geração textual. Ele reconhece marcadores, negação, temporalidade,
severidade, incerteza e experienciador em nível simples e auditável.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


MARKER_ONTOLOGY: dict[str, dict[str, Any]] = {
    "ideacao_suicida": {
        "positive_patterns": [r"pensamentos de morte", r"ideação suicida", r"ideacao suicida"],
        "negative_patterns": [r"nega ideação suicida", r"nega ideacao suicida", r"sem ideação", r"sem ideacao"],
    },
    "planejamento_suicida": {
        "positive_patterns": [r"planejamento de autoagressão", r"planejamento de autoagressao", r"planejamento suicida"],
        "negative_patterns": [r"sem planejamento", r"nega planejamento"],
    },
    "autoagressao_iminente": {
        "positive_patterns": [r"risco iminente de autoagressão", r"risco iminente de autoagressao", r"autoagressão iminente", r"autoagressao iminente"],
        "negative_patterns": [r"nega risco iminente", r"sem risco iminente"],
    },
    "risco_violencia": {
        "positive_patterns": [r"risco de comportamento agressivo", r"risco de violência", r"risco de violencia"],
        "negative_patterns": [r"nega risco de violência", r"nega risco de violencia"],
    },
    "sintomas_psicoticos": {
        "positive_patterns": [r"percepção alterada da realidade", r"percepcao alterada da realidade", r"ideias de referência", r"ideias de referencia", r"sintomas psicóticos", r"sintomas psicoticos"],
        "negative_patterns": [r"nega sintomas psicóticos", r"nega sintomas psicoticos"],
    },
    "uso_problematico_substancias": {
        "positive_patterns": [r"uso de álcool ou outras substâncias com prejuízo", r"uso de alcool ou outras substancias com prejuizo", r"uso problemático de substâncias", r"uso problematico de substancias"],
        "negative_patterns": [r"nega uso problemático", r"nega uso problematico"],
    },
    "internacao_previa": {
        "positive_patterns": [r"internação prévia", r"internacao previa"],
        "negative_patterns": [r"nega internação prévia", r"nega internacao previa"],
    },
    "agravamento_recente": {
        "positive_patterns": [r"piora recente", r"agravamento recente", r"piora dos sintomas nas últimas semanas", r"piora dos sintomas nas ultimas semanas"],
        "negative_patterns": [r"sem piora recente", r"nega piora recente"],
    },
    "suporte_social_baixo": {
        "positive_patterns": [r"rede de apoio limitada", r"suporte social limitado"],
        "negative_patterns": [r"rede de apoio disponível", r"rede de apoio disponivel"],
    },
    "comprometimento_funcional": {
        "positive_patterns": [r"dificuldade leve para manter", r"dificuldade moderada para manter", r"importante comprometimento para atividades"],
        "negative_patterns": [r"funcionalidade preservada"],
    },
}


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n", text.lower()) if part.strip()]


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) is not None for pattern in patterns)


def _temporal_label(sentence: str) -> str:
    if re.search(r"há dois anos|ha dois anos|prévia|previa|remoto|passado", sentence):
        return "remoto"
    if re.search(r"atual|no momento|nesta semana|recent[e]?|últimas semanas|ultimas semanas", sentence):
        return "atual"
    return "nao_especificado"


def _severity_label(marker: str, sentence: str) -> tuple[str, int]:
    if marker == "comprometimento_funcional":
        if "importante comprometimento" in sentence:
            return "importante", 3
        if "dificuldade moderada" in sentence:
            return "moderado", 2
        if "dificuldade leve" in sentence:
            return "leve", 1
        return "ausente", 0
    if re.search(r"iminente|intenso|importante|grave", sentence):
        return "alto", 3
    if re.search(r"moderad", sentence):
        return "moderado", 2
    if re.search(r"leve", sentence):
        return "leve", 1
    return "nao_especificado", 0


def _certainty_label(sentence: str) -> str:
    if re.search(r"possivelmente|pode|suspeita|incerto", sentence):
        return "incerto"
    return "afirmado"


def _experiencer_label(sentence: str) -> str:
    if re.search(r"mãe|mae|pai|familiar|família|familia", sentence):
        return "terceiro"
    return "paciente"


@dataclass
class RuleBasedClinicalExtractor:
    """Extrator de base com ontologia explícita e regra simples de negação."""

    ontology_version: str = "ontology_v1"
    extractor_id: str = "rule-dictionary-negation-v1"
    flip_rate: float = 0.0
    seed: int = 0

    def extract(self, narrative_frame: pd.DataFrame) -> pd.DataFrame:
        """Extrai marcadores e atributos de todas as narrativas recebidas."""
        required = {"patient_id", "narrativa_clinica"}
        missing = required - set(narrative_frame.columns)
        if missing:
            raise ValueError(f"Narrativas sem colunas necessárias: {sorted(missing)}")
        rng = np.random.default_rng(self.seed)
        rows: list[dict[str, Any]] = []

        for _, record in narrative_frame.iterrows():
            text = str(record["narrativa_clinica"])
            sentence_list = _sentences(text)
            row: dict[str, Any] = {
                "patient_id": record["patient_id"],
                "extractor_id": self.extractor_id,
                "ontology_version": self.ontology_version,
            }
            for marker, specification in MARKER_ONTOLOGY.items():
                positive_sentence = next((s for s in sentence_list if _contains_any(s, specification["positive_patterns"])), None)
                negative_sentence = next((s for s in sentence_list if _contains_any(s, specification["negative_patterns"])), None)

                # Regra de precedência: negação explícita do marcador tem prioridade sobre
                # uma correspondência genérica, mas não sobre expressão positiva específica
                # em uma sentença diferente. O texto-modelo não produz esse conflito.
                is_present = int(positive_sentence is not None and negative_sentence is None)
                is_negated = int(negative_sentence is not None)
                evidence_sentence = positive_sentence or negative_sentence or ""
                severity, severity_code = _severity_label(marker, evidence_sentence)

                # Ruído opcional é usado só em cenários de sensibilidade. Ele nunca é
                # ativado no cenário-base, permitindo medir degradacão controlada.
                if self.flip_rate > 0 and rng.random() < self.flip_rate:
                    is_present = 1 - is_present
                    is_negated = 1 - is_present if is_present == 0 else 0

                prefix = f"marcadores_extraidos_{marker}"
                row[f"{prefix}_present"] = is_present
                row[f"{prefix}_negated"] = is_negated
                row[f"{prefix}_temporality"] = _temporal_label(evidence_sentence)
                row[f"{prefix}_severity"] = severity
                row[f"{prefix}_severity_code"] = severity_code
                row[f"{prefix}_certainty"] = _certainty_label(evidence_sentence)
                row[f"{prefix}_experiencer"] = _experiencer_label(evidence_sentence)
                row[f"{prefix}_evidence"] = evidence_sentence
            rows.append(row)
        return pd.DataFrame(rows)


def extraction_reference_table(profiles: pd.DataFrame) -> pd.DataFrame:
    """Converte os marcadores marcadores_origem em formato comparável ao extrator.

    A referência sintética não substitui uma anotação humana; ela permite medir se o
    texto e o extrator preservam o cenário gerado. Anotadores independentes podem ser
    incorporados depois pelo script de validação.
    """
    result = pd.DataFrame({"patient_id": profiles["patient_id"]})
    for marker in MARKER_ONTOLOGY:
        if marker == "comprometimento_funcional":
            result[f"marcadores_origem_{marker}_present"] = (profiles["marcadores_origem_comprometimento_funcional"] > 0).astype(int)
            result[f"marcadores_origem_{marker}_severity_code"] = profiles["marcadores_origem_comprometimento_funcional"].astype(int)
        else:
            source = f"marcadores_origem_{marker}"
            if source not in profiles:
                raise ValueError(f"Marcador verdadeiro não encontrado: {source}")
            result[f"marcadores_origem_{marker}_present"] = profiles[source].astype(int)
            result[f"marcadores_origem_{marker}_severity_code"] = np.where(profiles[source].astype(int) == 1, 1, 0)
    return result
