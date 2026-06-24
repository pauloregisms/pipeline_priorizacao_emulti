# Architecture Decision Records (ADRs)

ADRs registram decisões de arquitetura e metodologia que têm impacto duradouro no projeto. Cada documento deve conter contexto, decisão, consequências e status.

## ADRs aceitos

| ADR | Decisão |
|---|---|
| [ADR-001](ADR-001-gerador-probabilistico.md) | usar gerador probabilístico estrutural, não GAN/CTGAN |
| [ADR-002](ADR-002-narrativas-desacopladas.md) | desacoplar geração de narrativas de fornecedores de LLM |
| [ADR-003](ADR-003-prioridade-simulada-ordinal.md) | usar prioridade simulada ordinal de quatro classes |
| [ADR-004](ADR-004-validacao-aninhada.md) | adotar validação aninhada e teste final isolado |
| [ADR-005](ADR-005-separacao-ztrue-zhat.md) | preservar a distinção entre `Z*` e `Zhat` |

## Quando criar novo ADR

Crie ADR para decisões difíceis de reverter ou que modifiquem o significado de dados, modelo, segurança, arquitetura ou interpretação dos resultados.

Use [ADR-TEMPLATE.md](ADR-TEMPLATE.md) como ponto de partida.
