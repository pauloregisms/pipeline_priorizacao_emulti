# Referência: scripts e interface de linha de comando

Todos os scripts aceitam, no mínimo:

```text
--config <arquivo_yaml>
--run-id <identificador_da_execucao>
```

`run_id` cria a raiz `artifacts/<run_id>/`.

## Etapas do pipeline

| Script | Função | Entrada principal | Saídas principais |
|---|---|---|---|
| `00_prepare_workspace.py` | prepara diretório e snapshot do ambiente | YAML | metadados de ambiente |
| `01_generate_profiles.py` | gera `X`, `V`, `U` e `Z*` | YAML | `profiles.csv` |
| `02_simulate_psychometrics.py` | gera itens e totais de `S` | perfis + YAML | `psychometrics.csv` |
| `03_quality_control_base.py` | valida faixas e consistência | perfis + escalas | tabelas e `quality_summary.json` |
| `04_generate_narratives.py` | gera `T` sem `Yref` | `X`, `S`, `Z*` | `narratives.jsonl` |
| `05_assign_reference_priority.py` | gera `Yref` | `X`, `S`, `Z*` | `priority_reference.csv` |
| `06_extract_markers.py` | extrai `Zhat` | narrativas | `markers_extracted.csv` |
| `07_create_annotation_sample.py` | cria amostra para dupla anotação | narrativas + estratos | template e auditoria |
| `08_validate_extraction.py` | mede extração contra `Z*` e anotadores | `Z*`, `Zhat`, CSVs opcionais | F1 e kappa |
| `09_build_analytical_datasets.py` | cria três conjuntos | artefatos anteriores | CSVs analíticos |
| `10_train_evaluate_models.py` | valida modelos | conjunto analítico | previsões, métricas, modelos |
| `11_explain_models.py` | coeficientes e SHAP no teste | modelos + teste | arquivos de explicação |
| `12_run_sensitivity.py` | executa cenários configurados | YAML | consolidação entre cenários |
| `13_generate_report.py` | monta síntese Markdown | artefatos | `report.md` |
| `14_export_priority_table.py` | consolida tabela ordenada da classificação final | perfis, escalas, `Zhat` e previsões do teste final | CSV, HTML e manifesto de visualização |

## Orquestrador

```bash
python scripts/run_pipeline.py --config config/base.yaml --run-id baseline
```

Opções adicionais:

| Opção | Efeito |
|---|---|
| `--skip-explanations` | não executa etapa 11 |
| `--skip-report` | não executa etapa 13 |
| `--stop-after <script>` | interrompe após script informado |

O orquestrador executa as etapas 00–10, depois 14, 11 e 13 salvo quando puladas. A etapa 12 é deliberadamente separada por executar réplicas adicionais.

## Opções específicas

### `08_validate_extraction.py`

```bash
python scripts/08_validate_extraction.py \
  --config config/base.yaml \
  --run-id baseline \
  --annotator-a annotation_a.csv \
  --annotator-b annotation_b.csv
```

### `10_train_evaluate_models.py`

```bash
python scripts/10_train_evaluate_models.py \
  --config config/base.yaml \
  --run-id baseline \
  --dataset 03_operacional_zhat \
  --models rule_baseline,ordinal_logit,random_forest,xgboost
```

`--dataset all` e `--models all` são os padrões.

### `11_explain_models.py`

O script aceita `--dataset` para escolher o conjunto analítico que terá coeficientes ou SHAP processados.

### `12_run_sensitivity.py`

```bash
python scripts/12_run_sensitivity.py \
  --config config/base.yaml \
  --run-id sensibilidade \
  --skip-modeling
```

`--skip-modeling` executa geração e construção de conjuntos até a etapa 09, útil para depuração rápida.

### `14_export_priority_table.py`

```bash
python scripts/14_export_priority_table.py \
  --config config/base.yaml \
  --run-id baseline \
  --dataset 03_operacional_zhat \
  --model best
```

Por padrão, `--model best` seleciona o maior `development_f1_macro` da validação aninhada, e não o maior desempenho do conjunto-teste final. Use `--include-reference` somente para auditoria da prova de conceito. A tabela é descrita em [Como visualizar a classificação final](../how-to/visualizar-classificacao-final.md).
