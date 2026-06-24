"""Etapa 0: cria diretórios, registra configuração e ambiente computacional."""

from __future__ import annotations

from pathlib import Path

from _bootstrap import common_parser
from emulti_pipeline.config import load_config
from emulti_pipeline.utils import environment_snapshot, json_hash, run_dir, setup_logging, write_json


def main() -> None:
    parser = common_parser("Prepara diretório de artefatos e metadados da execução.")
    args = parser.parse_args()
    config = load_config(args.config)
    logger = setup_logging("00_prepare_workspace")
    destination = run_dir(config, args.run_id)

    # Registrar a configuração imutável usada nesta execução evita que resultados
    # posteriores sejam associados acidentalmente a parâmetros alterados.
    write_json(destination / "run_metadata.json", {
        "run_id": args.run_id,
        "config_hash": json_hash(config),
        "config_path": str(Path(args.config).resolve()),
        "project": config["project"],
    })
    write_json(destination / "environment.json", environment_snapshot())
    logger.info("Workspace preparado em %s", destination)


if __name__ == "__main__":
    main()
