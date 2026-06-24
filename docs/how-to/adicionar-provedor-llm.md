# Como adicionar um provedor de LLM

A integração de um LLM é uma extensão futura. A versão atual usa `TemplateNarrativeGenerator`, sem chamadas externas. Um novo adaptador deve manter o contrato de entrada e saída para que as demais etapas do pipeline permaneçam independentes do fornecedor.

## Contrato obrigatório

O módulo `src/emulti_pipeline/narratives.py` define:

- `NarrativeRequest`: entrada permitida;
- `NarrativeResponse`: saída obrigatória;
- `BaseNarrativeGenerator`: interface a implementar.

`NarrativeRequest` contém apenas:

- `patient_id` sintético;
- `seed`;
- `structured_profile`;
- `psychometrics`;
- `true_markers`;
- `prompt_version`.

Ele **não** contém `Yref`, prioridade, códigos de prioridade, limiares nem informação equivalente.

## 1. Criar adaptador

Crie, por exemplo, `src/emulti_pipeline/narrative_providers/meu_provedor.py`:

```python
from emulti_pipeline.narratives import (
    BaseNarrativeGenerator,
    NarrativeRequest,
    NarrativeResponse,
)
from emulti_pipeline.utils import json_hash


class MeuProvedorNarrativeGenerator(BaseNarrativeGenerator):
    def __init__(self, model_id: str, api_key: str) -> None:
        self.model_id = model_id
        self.api_key = api_key

    def generate(self, request: NarrativeRequest) -> NarrativeResponse:
        # 1. validar que nenhuma chave proibida entrou no payload;
        # 2. montar prompt somente com request;
        # 3. chamar a API;
        # 4. validar conteúdo e estruturar retorno;
        # 5. devolver NarrativeResponse com metadados completos.
        raise NotImplementedError
```

Não copie este esqueleto como implementação final sem acrescentar tratamento de erros, retentativas, validação de formato e registro de metadados.

## 2. Construir o prompt de forma auditável

O prompt deve:

- pedir formato SOAP limitado aos campos necessários;
- proibir nomes, endereços, documentos e dados identificáveis;
- proibir criação de sintomas, diagnósticos ou eventos não presentes na entrada;
- solicitar linguagem clínica objetiva e concisa;
- ser versionado por arquivo ou identificador e ter hash registrado;
- não conter `Yref` ou pistas do rótulo.

## 3. Armazenar segredo com segurança

Use variável de ambiente:

```bash
export LLM_API_KEY='valor-local-nao-versionado'
```

Não versionar chave em YAML, código, notebook, log ou artefato. Veja [SECURITY.md](../../SECURITY.md).

## 4. Registrar metadados mínimos

O campo `generation_metadata` deve registrar, no mínimo:

```json
{
  "mode": "api",
  "provider": "identificador_do_provedor",
  "model_id": "identificador_exato_do_modelo",
  "model_version": "quando_disponivel",
  "request_timestamp_utc": "...",
  "temperature": 0.0,
  "max_tokens": 0,
  "prompt_hash": "...",
  "retry_count": 0,
  "forbidden_label_check": "passed"
}
```

Evite registrar cabeçalhos, credenciais ou payloads que não sejam necessários.

## 5. Tornar a escolha configurável

Após o adaptador ser testado, adicione uma chave de configuração como:

```yaml
narrative:
  provider: "template"  # ou "meu_provedor"
  generator_id: "template-simulator-v1"
```

Crie uma fábrica de geradores em vez de espalhar condicionais pelos scripts. Preserve `TemplateNarrativeGenerator` como modo local para testes reprodutíveis.

## 6. Validar antes de usar em experimento

- Compare uma amostra de narrativas com os atributos de origem.
- Verifique ausência de vazamento de prioridade.
- Verifique se o extrator independente ainda funciona.
- Registre modelo, parâmetros, versão do prompt e data.
- Execute uma réplica isolada antes de usar o adaptador em todos os cenários.

## Requisito de arquitetura

A implementação de um LLM não deve alterar a semântica de `Yref`, não deve acessar arquivos da etapa `05_priority` e não deve usar `u_latent_audit_only` como entrada textual.
