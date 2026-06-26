# Referência: provedor Gemini

## Implementação

O adaptador está em:

```text
src/emulti_pipeline/narrative_providers/gemini.py
```

A classe pública é `GeminiNarrativeGenerator`, implementando
`BaseNarrativeGenerator`. Ela é criada por `create_narrative_generator()` em
`emulti_pipeline.narratives` quando `narrative.provider: gemini` está ativo.

## Entrada autorizada

A entrada é sempre `NarrativeRequest`. O adaptador usa apenas:

```text
dados_estruturados
indicadores_psicometricos
marcadores_origem
```

`patient_id` e `seed` são usados para rastreabilidade e configuração do pedido,
mas não entram no conteúdo clínico do prompt. `prioridade_referencia`,
`prioridade_prevista`, `gravidade_latente_auditoria` e nomes equivalentes não
podem entrar no prompt.

## Formato enviado à API

A chamada usa a operação `client.models.generate_content()` do SDK
`google-genai` e solicita `application/json` com este esquema lógico:

```json
{
  "subjective": "texto do campo Subjetivo, sem o cabeçalho S",
  "assessment": "texto do campo Avaliação, sem o cabeçalho A"
}
```

O adaptador valida o JSON e monta a coluna de saída:

```text
S - <subjective>
A - <assessment>
```

## Metadados preservados

Cada linha de `narratives.jsonl` recebe `generation_metadata` semelhante a:

```json
{
  "mode": "gemini_api",
  "api_called": true,
  "provider": "gemini",
  "model_id": "gemini-3.1-flash-lite",
  "request_timestamp_utc": "...",
  "temperature": 1.0,
  "max_output_tokens": 500,
  "seed": 123,
  "prompt_hash": "...",
  "retry_count": 0,
  "forbidden_label_check": "passed",
  "response_format": "application/json",
  "usage": {}
}
```

Não são preservados a chave de API, cabeçalhos HTTP, prompt em texto integral ou
resposta bruta do fornecedor além da narrativa estruturada necessária ao estudo.

## Repetibilidade

O adaptador envia `seed` ao SDK, mas resultados de LLM devem ser tratados como
reprodutíveis por melhor esforço, não como determinísticos. Para cada execução,
preserve ao menos:

- YAML resolvido e identificador do cenário;
- `model_id` e `generator_id`;
- versão do prompt e `prompt_hash`;
- temperatura, limite de tokens e retentativas;
- timestamp da solicitação;
- narrativas e índices produzidos.

## Tratamento de erros

O adaptador faz `max_retries + 1` tentativas. A espera cresce de forma
exponencial a partir de `retry_backoff_seconds`. Se persistir erro de rede,
cota, formato ou resposta vazia, ele encerra a etapa com um erro que informa o
tipo da exceção, sem imprimir a mensagem do provedor ou credenciais.

## Dependência

A dependência é declarada no projeto:

```text
google-genai>=1.0,<2.0
```

O import do SDK é tardio. Dessa forma, quem executa `provider: template` não
precisa de chamada de rede nem de chave Gemini.
