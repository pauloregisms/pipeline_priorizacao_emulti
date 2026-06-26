"""Etapa 7: prepara uma amostra estratificada para anotação humana independente."""

from __future__ import annotations

import json

import pandas as pd

from _bootstrap import common_parser
from emulti_pipeline.config import load_config
from emulti_pipeline.utils import effective_seed, save_csv, setup_logging, stage_dir, write_json


def _load_jsonl(path) -> pd.DataFrame:
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return pd.DataFrame(records)


def main() -> None:
    parser = common_parser("Cria arquivo de anotação dupla estratificado por prioridade simulada.")
    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logging("07_create_annotation_sample")
    narratives = _load_jsonl(stage_dir(config, args.run_id, "04_narratives") / "narratives.jsonl")
    priority = pd.read_csv(stage_dir(config, args.run_id, "05_priority") / "prioridade_referencia.csv")
    profiles = pd.read_csv(stage_dir(config, args.run_id, "01_profiles") / "profiles.csv")
    merged = narratives.merge(priority[["patient_id", "prioridade_referencia"]], on="patient_id", how="inner")
    merged = merged.merge(profiles[["patient_id", "marcadores_origem_ideacao_suicida", "marcadores_origem_autoagressao_iminente", "marcadores_origem_sintomas_psicoticos"]], on="patient_id", how="inner")

    rng = pd.Series(range(len(merged))).sample(frac=1, random_state=effective_seed(config) + 5000).to_numpy()
    merged = merged.iloc[rng]
    selected = []
    n_per_priority = int(config["annotation"]["n_per_priority"])
    for label in ["baixa", "moderada", "alta", "urgente"]:
        subset = merged[merged["prioridade_referencia"] == label]
        selected.append(subset.head(min(n_per_priority, len(subset))))
    sample = pd.concat(selected, ignore_index=True).drop_duplicates("patient_id")

    # O rótulo de referência não é incluído no formulário entregue aos anotadores.
    # Ele permanece em arquivo de auditoria separado para estratificação e análise posterior.
    annotation = sample[["patient_id", "narrativa_clinica"]].copy()
    marker_columns = [
        "ideacao_suicida", "planejamento_suicida", "autoagressao_iminente", "risco_violencia",
        "sintomas_psicoticos", "uso_problematico_substancias", "internacao_previa",
        "agravamento_recente", "suporte_social_baixo", "comprometimento_funcional",
    ]
    for marker in marker_columns:
        annotation[f"{marker}_present"] = ""
        annotation[f"{marker}_negated"] = ""
        annotation[f"{marker}_temporality"] = ""
        annotation[f"{marker}_severity"] = ""
        annotation[f"{marker}_certainty"] = ""
        annotation[f"{marker}_experiencer"] = ""
    annotation["annotator_id"] = ""
    annotation["notes"] = ""

    output = stage_dir(config, args.run_id, "07_annotation")
    save_csv(annotation, output / "annotation_template.csv")
    save_csv(sample[["patient_id", "prioridade_referencia"]], output / "annotation_sampling_audit.csv")
    write_json(output / "annotation_instructions.json", {
        "instructions": "Dois anotadores independentes devem preencher o arquivo sem acesso a prioridade_referencia. Após a anotação, salvar versões separadas para comparação.",
        "fields": ["present", "negated", "temporality", "severity", "certainty", "experiencer"],
        "n_selected": int(len(annotation)),
    })
    logger.info("Amostra de anotação criada com %d narrativas", len(annotation))


if __name__ == "__main__":
    main()
