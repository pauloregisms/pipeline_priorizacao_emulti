# Referência: artefatos gerados

Cada execução usa `artifacts/<run_id>/`. Os diretórios preservam a ordem metodológica.

| Diretório | Arquivos relevantes | Finalidade |
|---|---|---|
| `00_workspace/` | snapshot do ambiente e configuração | reprodutibilidade computacional |
| `01_profiles/` | `profiles.csv`, metadados | `X`, `V`, `U`, `Z*` |
| `02_psychometrics/` | `psychometrics.csv`, metadados | itens e totais de `S` |
| `03_quality_control/` | tabelas de checagem, `quality_summary.json` | plausibilidade e consistência |
| `04_narratives/` | `narratives.jsonl`, índice e manifest | `T` e metadados do gerador |
| `05_priority/` | `priority_reference.csv`, metadata | `Yref` e evidências da matriz |
| `06_extraction/` | `markers_extracted.csv`, metadata | `Zhat` |
| `07_annotation/` | template, auditoria, instruções | anotação humana independente |
| `08_extraction_validation/` | métricas sintéticas, kappa e resumo | validação da extração |
| `09_analytical_sets/` | três CSVs analíticos | comparação de conjuntos |
| `10_modeling/` | modelos, previsões, métricas, bootstrap | validação interna |
| `11_explanations/` | coeficientes e SHAP | interpretabilidade no teste |
| `12_sensitivity/` | YAMLs temporários e resumo | robustez entre cenários |
| `13_report/` | `report.md` | síntese de execução |
| `14_priority_view/` | `classification_queue.csv`, `classification_queue.html`, manifesto | tabela ordenada para inspeção da classificação de perfis sintéticos |

## Convenções de preservação

- Use `run_id` único por cenário e réplica.
- Preserve junto com resultados finais: YAML, hash do commit, versão de dependências e logs de execução.
- Não comite toda a pasta `artifacts/` por padrão; selecione apenas exemplos sintéticos pequenos e deliberadamente versionados, se necessário.
- Nunca armazene dados reais, credenciais ou artefatos de API que possam conter material não permitido.

## Artefatos críticos para auditoria

Em uma análise formal, guarde pelo menos:

1. o YAML exato;
2. o snapshot do ambiente;
3. o manifesto de narrativas;
4. a matriz de prioridade e metadados;
5. os três conjuntos analíticos ou hashes deles;
6. previsões do teste final;
7. métricas e intervalos de confiança;
8. relatórios de sensibilidade;
9. versão da ontologia e formulários de anotação, quando usados.
