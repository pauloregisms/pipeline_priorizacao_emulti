# Pipeline Sintético de Priorização para e-Multi

> **Status:** prova de conceito de pesquisa. Este projeto gera e analisa dados inteiramente sintéticos; não usa prontuários, não recebe dados pessoais, não produz diagnóstico e não deve ser usado para priorização assistencial real.

Este repositório implementa uma simulação computacional para testar, em ambiente controlado, um fluxo de geração de perfis sintéticos, escalas psicométricas, narrativas clínicas SOAP, extração de marcadores e classificação de uma **prioridade de referência simulada** para encaminhamentos em saúde mental à e-Multi.

A finalidade é metodológica: avaliar plausibilidade, rastreabilidade, consistência interna e robustez do pipeline. Métricas elevadas neste repositório indicam apenas capacidade de recuperar relações e regras programadas no próprio cenário de simulação.

## Comece aqui

| Perfil | Próxima leitura |
|---|---|
| Novo desenvolvedor | [Visão geral do projeto](docs/explanation/visao-geral.md) e [Primeira execução](docs/tutorials/primeira-execucao.md) |
| Pesquisador que vai alterar o cenário | [Como criar um cenário](docs/how-to/criar-cenario.md) e [Configuração YAML](docs/reference/configuracao.md) |
| Desenvolvedor que vai integrar um LLM | [Como adicionar um provedor de LLM](docs/how-to/adicionar-provedor-llm.md) e [Contratos de dados](docs/reference/contratos-de-dados.md) |
| Pessoa responsável por regras de prioridade | [Matriz de prioridade](docs/reference/matriz-de-prioridade.md) e [ADR-003](docs/decisions/ADR-003-prioridade-simulada-ordinal.md) |
| Revisor de arquitetura | [arc42 resumido](docs/architecture/arc42.md) e diagramas [C4](docs/architecture/c4-contexto.md) |

A documentação completa está organizada no diretório [`docs/`](docs/index.md), seguindo uma combinação de **Docs-as-Code**, **Diátaxis**, **arc42/C4** e **Architecture Decision Records (ADRs)**.

## O que o pipeline faz

1. gera atributos sociodemográficos, psicossociais, clínicos e de utilização de serviços;
2. cria uma gravidade latente `U` para o gerador, preservada apenas para auditoria;
3. simula respostas por item e totais de PHQ-9, GAD-7 e IDATE-Estado;
4. verifica faixas e regras de consistência da base;
5. produz narrativa SOAP com um simulador textual desacoplado de qualquer API de LLM;
6. constrói `Yref`, uma prioridade de referência simulada, **após** gerar a narrativa;
7. extrai marcadores `Zhat` por uma linha de base baseada em dicionário e regras;
8. compara três conjuntos analíticos: `X+S`, `X+S+Z*` e `X+S+Zhat`;
9. avalia regra-base, regressão logística ordinal, Random Forest e XGBoost;
10. produz métricas de classificação, ordinalidade, calibração, robustez e explicabilidade;
11. consolida uma tabela ordenada de classificação para inspeção dos perfis sintéticos.

O mapa detalhado entre cada passo metodológico e os scripts está em [MAPA_DE_ETAPAS.md](MAPA_DE_ETAPAS.md) e na [referência de scripts](docs/reference/scripts.md).

## Garantias metodológicas essenciais

- `Yref` não é uma variável clínica real; é a saída da matriz de prioridade simulada.
- O gerador de narrativas recebe somente `X`, `S` e `Z*`; não recebe `Yref`, códigos, nomes de prioridade ou limiares que revelem o rótulo.
- A geração textual ocorre antes da criação de `Yref`.
- A gravidade latente `U` não entra nos conjuntos analíticos usados pelos classificadores.
- O extrator por regras é mantido como referência independente, inclusive quando uma futura versão usar LLM para extração.
- Parâmetros em `config/base.yaml` são **ilustrativos** e devem ser calibrados antes de qualquer análise acadêmica definitiva.

## Estrutura do repositório

```text
pipeline_priorizacao_emulti/
├── config/                    # parâmetros dos cenários de simulação
├── src/emulti_pipeline/       # módulos reutilizáveis do pipeline
├── scripts/                   # etapas executáveis 00–14 e orquestrador
├── artifacts/                 # saídas de execução (ignoradas pelo Git)
├── docs/                      # documentação versionada
├── .github/                   # modelos de colaboração no GitHub
├── README.md                  # entrada rápida para o projeto
├── CONTRIBUTING.md            # fluxo de contribuição
├── SECURITY.md                # dados, chaves e comunicação de vulnerabilidades
└── mkdocs.yml                 # navegação opcional para site de documentação
```

## Instalação local

Requisitos mínimos: Python 3.10 ou superior e `pip` atualizado.

```bash
python -m venv .venv
source .venv/bin/activate            # Linux/macOS
# .venv\Scripts\Activate.ps1         # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para a execução detalhada, consulte o [tutorial de primeira execução](docs/tutorials/primeira-execucao.md). Para uso em notebook, consulte [Google Colab](docs/tutorials/google-colab.md).

## Execução rápida

```bash
python scripts/run_pipeline.py --config config/base.yaml --run-id baseline
```

Para uma verificação rápida sem modelagem, explicabilidade ou relatório final:

```bash
python scripts/run_pipeline.py \
  --config config/base.yaml \
  --run-id smoke_test \
  --skip-explanations \
  --skip-report \
  --stop-after 03_quality_control_base.py
```

A análise de sensibilidade é executada separadamente, pois gera novas réplicas do pipeline:

```bash
python scripts/12_run_sensitivity.py --config config/base.yaml --run-id baseline
```

## Resultado esperado

Cada execução é gravada em `artifacts/<run_id>/`. Os principais produtos são descritos em [Artefatos gerados](docs/reference/artefatos.md):

- `01_profiles/profiles.csv` — atributos estruturados, `Z*` e coluna de auditoria do gerador;
- `02_psychometrics/psychometrics.csv` — itens e totais das escalas;
- `04_narratives/narratives.jsonl` — narrativas SOAP e metadados;
- `05_priority/priority_reference.csv` — `Yref` e evidências da matriz;
- `06_extraction/markers_extracted.csv` — marcadores extraídos `Zhat`;
- `09_analytical_sets/` — os três conjuntos analíticos;
- `10_modeling/` — previsões, métricas, modelos e intervalos;
- `11_explanations/` — coeficientes e/ou saídas SHAP;
- `13_report/report.md` — síntese automática da execução;
- `14_priority_view/classification_queue.csv` — tabela ordenada da classificação final para inspeção de perfis sintéticos.

Consulte também [Como visualizar a classificação final](docs/how-to/visualizar-classificacao-final.md).

## Integração futura com serviço de LLM

A geração narrativa é desacoplada em `src/emulti_pipeline/narratives.py`. A implementação atual, `TemplateNarrativeGenerator`, não realiza chamadas externas. Para integrar uma API, implemente `BaseNarrativeGenerator` e preserve os contratos `NarrativeRequest` e `NarrativeResponse`.

A integração futura deve:

- usar credenciais apenas por variáveis de ambiente ou cofre de segredos;
- registrar provedor, identificador do modelo, data, versão do prompt, parâmetros e política de retentativas;
- manter hash da entrada permitida e metadados da resposta;
- bloquear qualquer campo de prioridade ou informação equivalente;
- nunca enviar dados reais de pacientes por este projeto.

Veja o passo a passo em [Como adicionar um provedor de LLM](docs/how-to/adicionar-provedor-llm.md).

## Contribuição e documentação

Antes de contribuir, leia [CONTRIBUTING.md](CONTRIBUTING.md). Mudanças em scripts, parâmetros, contratos de dados ou regras de prioridade devem atualizar a documentação e, quando aplicável, um ADR ou o changelog.

> **Licença:** ainda não definida. Não reutilize ou redistribua o código fora do contexto autorizado pelo responsável pelo repositório até que uma licença seja escolhida.
