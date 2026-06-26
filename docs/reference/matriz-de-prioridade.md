# Referência: matriz de prioridade simulada

## Finalidade

A matriz gera `prioridade_referencia`, o alvo de referência para comparar regra-base e classificadores. Ela representa uma hipótese programada de priorização em um cenário sintético. Não representa necessidade clínica real nem deve orientar conduta.

## Classes ordinais

| Código | Rótulo | Interpretação no cenário |
|---:|---|---|
| 0 | baixa | menor prioridade simulada; não significa ausência de cuidado |
| 1 | moderada | necessidade de organização e acompanhamento no cenário |
| 2 | alta | prioridade simulada superior a baixa/moderada |
| 3 | urgente | classe de segurança simulada, não posição comum de fila |

## Regras de urgência

A classe `urgente` tem precedência determinística quando ocorre pelo menos uma condição:

1. ideação suicida com planejamento;
2. autoagressão iminente;
3. risco de violência;
4. sintomas psicóticos com comprometimento funcional importante.

Essas regras são implementadas em `assign_reference_priority()`.

## Evidência de alta prioridade

O cenário atual soma indicadores de:

- PHQ-9 acima de `phq_high`;
- GAD-7 acima de `gad_high`;
- IDATE-Estado acima de `stai_high`;
- comprometimento funcional moderado ou importante;
- uso problemático de substâncias;
- agravamento recente;
- vulnerabilidade social acima de `vulnerability_high`;
- suporte social baixo.

A prioridade é `alta` quando o escore composto não urgente atinge o limiar implementado. O código também inclui um termo de ruído não urgente pré-especificado.

## Evidência de prioridade moderada

O cenário atual agrega:

- PHQ-9 acima de `phq_moderate`;
- GAD-7 acima de `gad_moderate`;
- IDATE-Estado acima de `stai_moderate`;
- comprometimento funcional leve ou maior;
- agravamento recente;
- suporte social baixo.

## Fonte de verdade e dívida técnica

A referência `prioridade_referencia` lê valores do YAML. Já a regra-base operacional possui limiares codificados em `priority.py`. Esse acoplamento deve ser eliminado antes de qualquer calibração final.

### Refatoração recomendada

Criar uma estrutura única, por exemplo uma função ou objeto `PriorityRuleSet`, que:

- leia os parâmetros do YAML;
- seja usada pela matriz de referência e pela regra-base;
- exponha explicitamente quais marcadores são observáveis em cada conjunto analítico;
- tenha testes de unidade para regras urgentes e casos limítrofes.

## Processo recomendado de revisão

1. Propor critérios e fontes.
2. Submeter critérios a revisão de conteúdo por especialistas.
3. Congelar versão da matriz antes da modelagem.
4. Registrar alterações em ADR e changelog quando forem estruturais.
5. Rodar cenários de sensibilidade com a matriz alterada.
