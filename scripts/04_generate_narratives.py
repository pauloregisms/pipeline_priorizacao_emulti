"""Etapa 4: gera narrativas SOAP simuladas por interface desacoplada de LLM."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from _bootstrap import common_parser
from emulti_pipeline.config import load_config
from emulti_pipeline.narratives import NarrativeRequest, TemplateNarrativeGenerator
from emulti_pipeline.utils import effective_seed, setup_logging, stage_dir, write_json


def _record_to_request(profile: pd.Series, scales: pd.Series, prompt_version: str) -> NarrativeRequest:
    """Monta a entrada permitida pelo gerador textual.

    O código seleciona explicitamente apenas X, S e Z*. Não importa arquivos de
    prioridade e não aceita ``y_ref`` como campo de entrada.
    """
    structured_columns = [
        "age_years", "gender_category", "education", "income_brl", "food_insecurity",
        "poor_housing", "social_vulnerability", "mental_health_history", "chronic_condition",
        "recent_service_contact",
    ]
    structured_profile = {column: profile[column] for column in structured_columns}
    psychometric_summary = {
        "phq9_total": int(scales["phq9_total"]),
        "gad7_total": int(scales["gad7_total"]),
        "idate_estado_total": int(scales["idate_estado_total"]),
    }
    true_markers = {
        "ideacao_suicida": int(profile["ztrue_ideacao_suicida"]),
        "planejamento_suicida": int(profile["ztrue_planejamento_suicida"]),
        "autoagressao_iminente": int(profile["ztrue_autoagressao_iminente"]),
        "risco_violencia": int(profile["ztrue_risco_violencia"]),
        "sintomas_psicoticos": int(profile["ztrue_sintomas_psicoticos"]),
        "uso_problematico_substancias": int(profile["ztrue_uso_problematico_substancias"]),
        "internacao_previa": int(profile["ztrue_internacao_previa"]),
        "agravamento_recente": int(profile["ztrue_agravamento_recente"]),
        "suporte_social_baixo": int(profile["ztrue_suporte_social_baixo"]),
        "comprometimento_funcional": int(profile["ztrue_comprometimento_funcional"]),
    }
    return NarrativeRequest(
        patient_id=str(profile["patient_id"]),
        seed=int(profile["seed"]) + 2000,
        structured_profile=structured_profile,
        psychometrics=psychometric_summary,
        true_markers=true_markers,
        prompt_version=prompt_version,
    )


def main() -> None:
    parser = common_parser("Gera narrativas clínicas sintéticas sem vazamento de rótulo.")
    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logging("04_generate_narratives")
    profiles = pd.read_csv(stage_dir(config, args.run_id, "01_profiles") / "profiles.csv")
    psychometrics = pd.read_csv(stage_dir(config, args.run_id, "02_psychometrics") / "psychometrics.csv")
    merged = profiles.merge(psychometrics, on="patient_id", how="inner", validate="one_to_one")

    # Invariante explícita: esta etapa deve ocorrer antes da criação de y_ref e não pode
    # receber nenhuma coluna que represente prioridade.
    if any("priority" in column.lower() or "y_ref" in column.lower() for column in merged.columns):
        raise ValueError("Foram detectadas colunas de prioridade na entrada da geração textual.")

    generator = TemplateNarrativeGenerator(config["narrative"]["generator_id"])
    output = stage_dir(config, args.run_id, "04_narratives")
    output_file = output / "narratives.jsonl"
    rows = []
    with output_file.open("w", encoding="utf-8") as handle:
        for _, record in merged.iterrows():
            request = _record_to_request(record, record, config["narrative"]["prompt_version"])
            response = generator.generate(request)
            row = response.to_dict()
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)

    # CSV compacto facilita inspeção humana; JSONL preserva a resposta completa e os metadados.
    pd.DataFrame(rows).drop(columns=["generation_metadata"], errors="ignore").to_csv(output / "narratives_index.csv", index=False, encoding="utf-8")
    write_json(output / "narrative_generation_manifest.json", {
        "generator_id": config["narrative"]["generator_id"],
        "prompt_version": config["narrative"]["prompt_version"],
        "narratives": len(rows),
        "api_called": False,
        "forbidden_input_keys": config["narrative"]["forbidden_input_keys"],
        "seed_base": effective_seed(config),
    })
    logger.info("Foram geradas %d narrativas sintéticas em %s", len(rows), output_file)


if __name__ == "__main__":
    main()
