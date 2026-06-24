# C4 — Diagrama de componentes

```mermaid
flowchart LR
    CFG["config.py\ncarrega YAML"]
    SIM["simulation.py\nX, V, U, Z*, S"]
    QC["quality.py\nfaixas e consistência"]
    NAR["narratives.py\nNarrativeRequest/Response"]
    PRI["priority.py\nYref e regra-base"]
    EXT["extraction.py\nZhat por ontologia"]
    FEAT["features.py\nconjuntos analíticos"]
    MOD["models.py\nmodelos e preprocessamento"]
    EVA["evaluation.py\nmétricas e bootstrap"]
    UTL["utils.py\nsementes, caminhos, hashes"]

    CFG --> SIM
    CFG --> QC
    CFG --> NAR
    CFG --> PRI
    CFG --> EXT
    CFG --> FEAT
    CFG --> MOD
    CFG --> EVA
    UTL --> SIM
    UTL --> NAR
    UTL --> PRI
    UTL --> EVA
    SIM --> QC
    SIM --> NAR
    SIM --> PRI
    NAR --> EXT
    PRI --> FEAT
    EXT --> FEAT
    FEAT --> MOD
    MOD --> EVA
```

## Interfaces críticas

### Geração narrativa

`narratives.py` recebe `NarrativeRequest` e produz `NarrativeResponse`. Nenhuma outra etapa deve depender de API ou fornecedor específico.

### Prioridade

`priority.py` produz `Yref` com base em `X`, `S` e `Z*`. Ele não deve acessar narrativa ou `Zhat` para construir a referência.

### Extração

`extraction.py` produz `Zhat` apenas a partir de texto. A comparação com `Z*` ocorre na validação, não durante a extração.

### Modelagem

`features.py` remove `u_latent_audit_only` e cria três conjuntos. `models.py` realiza pré-processamento dentro dos folds, e `evaluation.py` produz métricas a partir de predições.

## Regra de dependência

Dependências devem fluir da configuração e dos módulos de geração para artefatos, e não no sentido contrário. Em particular:

```text
Yref não → gerador de narrativa
U não → classificadores
Z* não substitui Zhat no conjunto operacional
```
