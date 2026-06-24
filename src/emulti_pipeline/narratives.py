"""Interface desacoplada e simulador de geração de narrativas clínicas.

A classe ``TemplateNarrativeGenerator`` é uma simulação local de um serviço de LLM.
Ela existe para permitir testes end-to-end sem chamar APIs, mantendo estáveis os
contratos de entrada e saída. Uma implementação futura de API deve herdar de
``BaseNarrativeGenerator`` e retornar os mesmos campos de ``NarrativeResponse``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .utils import json_hash


@dataclass(frozen=True)
class NarrativeRequest:
    """Dados permitidos para geração da narrativa de um perfil sintético.

    ``priority`` e qualquer campo que revele o rótulo são proibidos por construção.
    """

    patient_id: str
    seed: int
    structured_profile: dict[str, Any]
    psychometrics: dict[str, Any]
    true_markers: dict[str, Any]
    prompt_version: str


@dataclass(frozen=True)
class NarrativeResponse:
    """Contrato de retorno preservado para simulador local ou API futura."""

    patient_id: str
    narrative_id: str
    subjective: str
    assessment: str
    full_text: str
    generator_id: str
    prompt_version: str
    input_hash: str
    generation_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseNarrativeGenerator(ABC):
    """Interface mínima que qualquer adaptador de LLM futuro deverá implementar."""

    @abstractmethod
    def generate(self, request: NarrativeRequest) -> NarrativeResponse:
        """Gera uma narrativa sem receber rótulo de prioridade ou informação equivalente."""


def _score_description(phq: int, gad: int, stai: int) -> str:
    """Converte escores em descrição clínica genérica, sem declarar prioridade."""
    if phq >= 20 or gad >= 15 or stai >= 65:
        return "refere sofrimento emocional intenso, com sintomas persistentes de humor deprimido e ansiedade"
    if phq >= 10 or gad >= 10 or stai >= 50:
        return "refere sintomas de ansiedade e humor deprimido com repercussão no cotidiano"
    if phq >= 5 or gad >= 5:
        return "refere sintomas leves e oscilantes de ansiedade ou humor"
    return "refere sintomas emocionais leves e atualmente estáveis"


def _functional_description(level: int) -> str:
    descriptions = {
        0: "mantém funcionalidade preservada nas atividades habituais",
        1: "relata dificuldade leve para manter as atividades habituais",
        2: "relata dificuldade moderada para manter atividades cotidianas",
        3: "relata importante comprometimento para atividades cotidianas",
    }
    return descriptions.get(int(level), "não foi possível caracterizar a funcionalidade")


class TemplateNarrativeGenerator(BaseNarrativeGenerator):
    """Gerador local, determinístico por semente, que simula a saída de uma LLM.

    O uso de variantes linguísticas torna a extração mais realista do que uma simples
    cópia de colunas. Ainda assim, o texto é estritamente condicionado aos atributos
    permitidos da requisição.
    """

    def __init__(self, generator_id: str = "template-simulator-v1") -> None:
        self.generator_id = generator_id

    def generate(self, request: NarrativeRequest) -> NarrativeResponse:
        # Defesa metodológica: qualquer chave proibida indica vazamento de rótulo.
        forbidden = {"y_ref", "priority", "prioridade", "priority_code"}
        request_keys = set(request.structured_profile) | set(request.psychometrics) | set(request.true_markers)
        leaked = forbidden.intersection(request_keys)
        if leaked:
            raise ValueError(f"A requisição para narrativa contém campos proibidos: {sorted(leaked)}")

        rng = np.random.default_rng(request.seed)
        p = request.structured_profile
        s = request.psychometrics
        z = request.true_markers

        symptom_text = _score_description(
            int(s["phq9_total"]), int(s["gad7_total"]), int(s["idate_estado_total"])
        )
        function_text = _functional_description(int(z["comprometimento_funcional"]))

        subjective_parts = [
            symptom_text,
            function_text,
        ]
        assessment_parts = [
            "Quadro compatível, no cenário sintético, com necessidade de acompanhamento conforme evolução e rede de suporte.",
        ]

        # As frases abaixo são selecionadas somente a partir de Z*. Não há acesso a Yref.
        if int(z["ideacao_suicida"]) == 1:
            if int(z["planejamento_suicida"]) == 1:
                subjective_parts.append("Relata pensamentos de morte atuais e planejamento de autoagressão.")
            else:
                subjective_parts.append("Relata pensamentos de morte atuais, sem planejamento ou intenção informados.")
        else:
            subjective_parts.append("Nega ideação suicida atual.")

        if int(z["autoagressao_iminente"]) == 1:
            subjective_parts.append("Relata risco iminente de autoagressão no momento da consulta.")
        if int(z["risco_violencia"]) == 1:
            subjective_parts.append("Refere irritabilidade intensa e risco de comportamento agressivo recente.")
        if int(z["sintomas_psicoticos"]) == 1:
            subjective_parts.append("Descreve percepção alterada da realidade e ideias de referência recentes.")
        if int(z["uso_problematico_substancias"]) == 1:
            subjective_parts.append("Relata uso de álcool ou outras substâncias com prejuízo percebido.")
        if int(z["internacao_previa"]) == 1:
            subjective_parts.append("Informa internação prévia relacionada a sofrimento psíquico.")
        if int(z["agravamento_recente"]) == 1:
            subjective_parts.append("Relata piora recente dos sintomas nas últimas semanas.")
        if int(z["suporte_social_baixo"]) == 1:
            subjective_parts.append("Refere rede de apoio limitada no momento.")
        else:
            subjective_parts.append("Refere presença de alguma rede de apoio disponível.")

        # Pequena variação superficial do texto, sem introduzir informação clínica nova.
        opening = rng.choice(["Usuário", "Pessoa acompanhada", "Paciente fictício"])
        subjective = f"{opening}: " + " ".join(subjective_parts)
        assessment = "Avaliação: " + " ".join(assessment_parts)
        full_text = f"S - {subjective}\nA - {assessment}"

        input_payload = {
            "patient_id": request.patient_id,
            "seed": request.seed,
            "structured_profile": request.structured_profile,
            "psychometrics": request.psychometrics,
            "true_markers": request.true_markers,
            "prompt_version": request.prompt_version,
        }
        input_hash = json_hash(input_payload)
        narrative_id = f"NAR-{request.patient_id}-{input_hash[:10]}"

        return NarrativeResponse(
            patient_id=request.patient_id,
            narrative_id=narrative_id,
            subjective=subjective,
            assessment=assessment,
            full_text=full_text,
            generator_id=self.generator_id,
            prompt_version=request.prompt_version,
            input_hash=input_hash,
            generation_metadata={
                "mode": "simulated_template",
                "random_seed": request.seed,
                "api_called": False,
                "forbidden_label_check": "passed",
            },
        )


class FutureApiNarrativeGenerator(BaseNarrativeGenerator):
    """Esqueleto explícito para futura integração com API.

    Esta classe não chama serviços externos. Ela documenta o ponto de extensão e evita
    misturar código de credenciais/HTTP com o restante do pipeline.
    """

    def generate(self, request: NarrativeRequest) -> NarrativeResponse:  # pragma: no cover
        raise NotImplementedError(
            "Implemente um adaptador de API que herde de BaseNarrativeGenerator. "
            "O adaptador deve respeitar NarrativeRequest/NarrativeResponse e nunca enviar y_ref."
        )
