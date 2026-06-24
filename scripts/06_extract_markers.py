"""Etapa 6: extrai Z-hat das narrativas por regras, dicionário e negação simples."""

from __future__ import annotations

import json

import pandas as pd

from _bootstrap import common_parser
from emulti_pipeline.config import load_config
from emulti_pipeline.extraction import RuleBasedClinicalExtractor
from emulti_pipeline.utils import effective_seed, save_csv, setup_logging, stage_dir, write_json


def _load_jsonl(path) -> pd.DataFrame:
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return pd.DataFrame(records)


def main() -> None:
    parser = common_parser("Extrai entidades e atributos clínicos das narrativas sintéticas.")
    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logging("06_extract_markers")
    narratives = _load_jsonl(stage_dir(config, args.run_id, "04_narratives") / "narratives.jsonl")

    extractor = RuleBasedClinicalExtractor(
        ontology_version=config["extraction"]["ontology_version"],
        extractor_id=config["extraction"]["extractor_id"],
        flip_rate=float(config["simulation"].get("extraction_flip_rate", 0.0)),
        seed=effective_seed(config) + 4000,
    )
    extracted = extractor.extract(narratives)
    output = stage_dir(config, args.run_id, "06_extraction")
    save_csv(extracted, output / "markers_extracted.csv")
    write_json(output / "extraction_manifest.json", {
        "extractor_id": extractor.extractor_id,
        "ontology_version": extractor.ontology_version,
        "extraction_flip_rate": extractor.flip_rate,
        "note": "Linha de base independente da geração textual; não utiliza y_ref.",
    })
    logger.info("Marcadores extraídos para %d narrativas", len(extracted))


if __name__ == "__main__":
    main()
