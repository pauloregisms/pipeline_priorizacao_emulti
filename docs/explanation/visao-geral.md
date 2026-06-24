# Visão geral do projeto

## Problema abordado

O projeto explora, em ambiente de simulação, como um pipeline computacional pode organizar informações estruturadas e narrativas clínicas para recuperar uma **prioridade de referência simulada** de encaminhamentos em saúde mental à e-Multi.

A motivação conceitual é a necessidade de organizar demandas de saúde mental na Atenção Primária à Saúde. Porém, o software não mede o fluxo real de um serviço, não usa decisões de profissionais e não estima prioridade clínica de pessoas reais.

## O que é avaliado

O pipeline avalia cinco propriedades:

1. **Plausibilidade:** faixas, distribuições, associações esperadas e regras de consistência da base sintética.
2. **Rastreabilidade:** identificação de sementes, parâmetros, versões de prompt e artefatos de cada execução.
3. **Preservação de informação:** diferença entre marcadores verdadeiros do gerador `Z*` e marcadores recuperados do texto `Zhat`.
4. **Recuperação de uma regra simulada:** concordância de modelos com `Yref`.
5. **Robustez:** mudança de resultados entre sementes, dados faltantes, ruído na extração e cenários configurados.

## O que não é avaliado

Este projeto não demonstra:

- validade clínica;
- acurácia em pacientes reais;
- benefício assistencial;
- segurança de uso em serviços;
- redução de filas ou tempo de espera;
- equidade em população observada;
- desempenho temporal, geográfico ou externo.

## Vocabulário essencial

| Símbolo / termo | Significado | Pode entrar no classificador? |
|---|---|---|
| `X` | atributos estruturados disponíveis no cenário conceitual de encaminhamento | Sim |
| `V` | índice sintético de vulnerabilidade social derivado de componentes de `X` | Sim, por meio de `social_vulnerability` |
| `U` | gravidade latente interna ao gerador | Não |
| `S` | itens e totais psicométricos simulados | Sim; cenário-base usa totais |
| `Z*` | marcadores clínicos verdadeiros gerados no cenário | Somente no conjunto de limite superior |
| `T` | narrativa SOAP sintética | Não diretamente; origina `Zhat` |
| `Zhat` | marcadores extraídos de `T` | Sim, no conjunto operacional |
| `Yref` | prioridade de referência simulada | É o alvo; não entra como preditor |
| `Yhat` | previsão produzida por regra ou modelo | Resultado da modelagem |

## Fronteiras éticas e técnicas

O repositório deve permanecer em uma fronteira segura: dados e narrativas inteiramente sintéticos, sem integração com PEC, sem recomendação automatizada de conduta e sem inferências sobre pessoas reais.

A geração de narrativa é desacoplada de fornecedores de LLM para permitir testes sem API e para evitar que a metodologia dependa de uma ferramenta comercial. O simulador atual é determinístico por semente e serve como substituto de um provedor externo durante os experimentos iniciais.

## Próximas leituras

- [Metodologia e fluxo](metodologia-e-fluxo.md)
- [Limites e salvaguardas](limites-e-salvaguardas.md)
- [C4 — Componentes](../architecture/c4-componentes.md)
