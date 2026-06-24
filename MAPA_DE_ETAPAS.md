# Mapa entre metodologia e scripts

| Etapa metodológica | Script | Entrada principal | Saída principal |
|---|---|---|---|
| Reprodutibilidade e ambiente | `00_prepare_workspace.py` | YAML de configuração | metadados da execução, versão de bibliotecas |
| Geração de X, V, U e Z* | `01_generate_profiles.py` | parâmetros estruturais | `profiles.csv` |
| Itens e totais psicométricos | `02_simulate_psychometrics.py` | perfis, parâmetros de escalas | `psychometrics.csv` |
| Plausibilidade e consistência | `03_quality_control_base.py` | perfis e escalas | checagens e sumário de qualidade |
| Narrativa SOAP sintética | `04_generate_narratives.py` | X, S e Z*; nunca Yref | `narratives.jsonl` |
| Matriz de prioridade simulada | `05_assign_reference_priority.py` | X, S, Z* e regras protocoladas | `priority_reference.csv` |
| PLN independente | `06_extract_markers.py` | narrativas | `markers_extracted.csv` com Z-hat |
| Anotação humana | `07_create_annotation_sample.py` | narrativas e estratos | formulário de dupla anotação |
| Validação da extração | `08_validate_extraction.py` | Z*, Z-hat e anotações opcionais | precisão, recall, F1 e concordância |
| Conjuntos analíticos | `09_build_analytical_datasets.py` | X, S, Z*, Z-hat e Yref | três conjuntos comparáveis |
| Validação interna | `10_train_evaluate_models.py` | conjuntos analíticos | métricas, previsões, modelos e ICs |
| Interpretabilidade | `11_explain_models.py` | modelos e teste final | coeficientes/SHAP no conjunto-teste |
| Robustez | `12_run_sensitivity.py` | cenários do YAML | desempenho entre cenários |
| Relatório | `13_generate_report.py` | artefatos das etapas anteriores | `report.md` |
| Visualização simplificada | `14_export_priority_table.py` | previsões finais + X, S e Zhat | tabela CSV/HTML ordenada para inspeção de perfis sintéticos |

## Garantia contra vazamento de rótulo

A geração de narrativas é executada antes do script que cria `Yref`. O contrato da classe `NarrativeRequest`, em `src/emulti_pipeline/narratives.py`, não possui campo de prioridade. Além disso, `04_generate_narratives.py` interrompe a execução se detectar colunas com nomes que sugiram rótulo de prioridade.

## Ponto de extensão para API de LLM

`TemplateNarrativeGenerator` é o simulador local. Para trocar por um serviço real, criar uma classe que herde de `BaseNarrativeGenerator`, receba `NarrativeRequest` e devolva `NarrativeResponse`. Não misturar credenciais, chamadas HTTP ou configuração do provedor com os scripts de geração/extração.
