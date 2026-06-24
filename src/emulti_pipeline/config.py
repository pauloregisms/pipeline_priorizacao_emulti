"""Leitura e validação leve da configuração do pipeline."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Lê um arquivo YAML de configuração e devolve um dicionário independente."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("A configuração YAML deve conter um objeto/dicionário no nível superior.")
    return copy.deepcopy(config)
