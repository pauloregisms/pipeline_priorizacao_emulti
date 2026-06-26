"""Etapa 8: avalia marcadores_extraidos contra marcadores_origem e aceita anotações humanas futuras."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

from _bootstrap import common_parser
from emulti_pipeline.config import load_config
from emulti_pipeline.extraction import MARKER_ONTOLOGY, extraction_reference_table
from emulti_pipeline.utils import save_csv, setup_logging, stage_dir, write_json


def _metric_row(marker: str, reference: np.ndarray, predicted: np.ndarray) -> dict[str, float | str | int]:
    precision, recall, f1, _ = precision_recall_fscore_support(reference, predicted, average="binary", zero_division=0)
    return {
        "marker": marker,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "positive_support": int(np.sum(reference == 1)),
    }


def _cohen_kappa_binary(left: np.ndarray, right: np.ndarray) -> float:
    # Implementação mínima para evitar obrigar uso de bibliotecas adicionais.
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(left, right))


def main() -> None:
    parser = common_parser("Valida a extração contra marcadores_origem e anotações humanas quando disponíveis.")
    parser.add_argument("--annotator-a", default=None, help="CSV opcional preenchido pelo anotador A.")
    parser.add_argument("--annotator-b", default=None, help="CSV opcional preenchido pelo anotador B.")
    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logging("08_validate_extraction")
    profiles = pd.read_csv(stage_dir(config, args.run_id, "01_profiles") / "profiles.csv")
    extracted = pd.read_csv(stage_dir(config, args.run_id, "06_extraction") / "marcadores_extraidos.csv")
    reference = extraction_reference_table(profiles)
    merged = reference.merge(extracted, on="patient_id", how="inner", validate="one_to_one")

    metrics = []
    for marker in MARKER_ONTOLOGY:
        true_col = f"marcadores_origem_{marker}_present"
        pred_col = f"marcadores_extraidos_{marker}_present"
        metrics.append(_metric_row(marker, merged[true_col].to_numpy(), merged[pred_col].to_numpy()))
    metrics_frame = pd.DataFrame(metrics)

    output = stage_dir(config, args.run_id, "08_extraction_validation")
    save_csv(metrics_frame, output / "synthetic_reference_metrics.csv")

    annotation_summary: dict[str, object] = {"available": False}
    if args.annotator_a and args.annotator_b:
        ann_a = pd.read_csv(args.annotator_a)
        ann_b = pd.read_csv(args.annotator_b)
        joined = ann_a.merge(ann_b, on="patient_id", suffixes=("_a", "_b"), validate="one_to_one")
        kappa_rows = []
        for marker in MARKER_ONTOLOGY:
            left = pd.to_numeric(joined[f"{marker}_present_a"], errors="coerce").fillna(-1).astype(int)
            right = pd.to_numeric(joined[f"{marker}_present_b"], errors="coerce").fillna(-1).astype(int)
            valid = (left >= 0) & (right >= 0)
            if valid.any():
                kappa_rows.append({"marker": marker, "cohen_kappa_present": _cohen_kappa_binary(left[valid], right[valid]), "n": int(valid.sum())})
        kappa_frame = pd.DataFrame(kappa_rows)
        save_csv(kappa_frame, output / "inter_annotator_agreement.csv")
        annotation_summary = {"available": True, "n_joined": int(len(joined)), "metrics_file": "inter_annotator_agreement.csv"}

    write_json(output / "validation_summary.json", {
        "synthetic_reference_mean_f1": float(metrics_frame["f1"].mean()),
        "synthetic_reference_mean_recall": float(metrics_frame["recall"].mean()),
        "human_annotation": annotation_summary,
        "interpretation": "marcadores_origem é referência do gerador; anotação humana independente deve complementar esta avaliação.",
    })
    logger.info("Validação da extração concluída. F1 médio contra marcadores_origem: %.3f", metrics_frame["f1"].mean())


if __name__ == "__main__":
    main()
