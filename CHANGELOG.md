# Changelog

Este arquivo registra mudanças relevantes para quem executa, estende, revisa ou reproduz o pipeline.

O formato segue a convenção **Keep a Changelog** de forma simplificada. Versões futuras devem separar mudanças em `Adicionado`, `Alterado`, `Corrigido`, `Removido` e `Segurança` quando aplicável.

## [Não lançado]

### Adicionado

- Estrutura de documentação Docs-as-Code em `docs/`.
- Organização por Diátaxis: explicações, tutoriais, guias práticos e referências.
- Documentação de arquitetura arc42 e diagramas C4 em Mermaid.
- Registros de decisões arquiteturais (ADRs).
- Guia de contribuição, política de segurança e modelo de pull request.
- Configuração opcional de navegação para MkDocs.
- Etapa 14 para consolidar uma tabela ordenada de classificação final de perfis sintéticos em CSV e HTML.
- Funções reutilizáveis de visualização em `emulti_pipeline.visualization`.
- Guia de uso da tabela no terminal e no Google Colab.

## [0.1.0] — 2026-06-24

### Adicionado

- Pipeline inicial de simulação probabilística estrutural.
- Simulação de perfis sintéticos e escalas PHQ-9, GAD-7 e IDATE-Estado.
- Gerador de narrativas SOAP simuladas e desacopladas de APIs de LLM.
- Regra de prioridade de referência simulada em quatro categorias.
- Extrator de marcadores baseado em dicionário e regras de negação.
- Conjuntos analíticos `X+S`, `X+S+Z*` e `X+S+Zhat`.
- Modelagem com regra-base, regressão logística ordinal, Random Forest e XGBoost.
- Métricas de classificação, calibração, robustez e explicabilidade.
