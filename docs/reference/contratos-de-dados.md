# Referência: contratos de dados

Este documento define formatos e fronteiras de dados que novos componentes devem respeitar.

## Notação

| Nome | Papel |
|---|---|
| `X` | atributos estruturados observáveis antes do encaminhamento conceitual |
| `S` | escalas psicométricas simuladas |
| `Z*` | marcadores verdadeiros do gerador |
| `T` | narrativa SOAP sintética |
| `Zhat` | marcadores extraídos de `T` |
| `Yref` | prioridade de referência simulada |
| `Yhat` | previsão de regra ou classificador |

## `NarrativeRequest`

Definido em `src/emulti_pipeline/narratives.py`.

```python
@dataclass(frozen=True)
class NarrativeRequest:
    patient_id: str
    seed: int
    structured_profile: dict[str, Any]
    psychometrics: dict[str, Any]
    true_markers: dict[str, Any]
    prompt_version: str
```

### Invariantes

- `patient_id` deve ser sintético.
- `seed` deve permitir reprodução da geração textual simulada.
- `structured_profile`, `psychometrics` e `true_markers` podem conter apenas informação permitida no cenário.
- Não pode conter `y_ref`, `priority`, `prioridade`, `priority_code` ou equivalente.
- A implementação do gerador deve falhar explicitamente se detectar chave proibida.

## `NarrativeResponse`

```python
@dataclass(frozen=True)
class NarrativeResponse:
    patient_id: str
    narrative_id: str
    subjective: str
    assessment: str
    full_text: str
    generator_id: str
    prompt_version: str
    input_hash: str
    generation_metadata: dict[str, Any]
```

### Requisitos

- `full_text` deve ser resultado coerente com `subjective` e `assessment`.
- `input_hash` deve ser calculado a partir do payload permitido.
- `generation_metadata` deve permitir auditoria sem expor credenciais.
- Uma API futura deve registrar modelo, versão, parâmetros e política de retentativa.

## Perfil sintético (`profiles.csv`)

Campos centrais:

| Grupo | Campos principais |
|---|---|
| Identificação | `patient_id`, `seed` |
| Sociodemográficos | `age_years`, `gender_category`, `education`, `income_brl`, `income_normalized` |
| Psicossociais | `food_insecurity`, `poor_housing`, `social_vulnerability` |
| Clínicos/uso de serviço | `mental_health_history`, `chronic_condition`, `recent_service_contact` |
| Auditoria | `u_latent_audit_only` — proibido nos classificadores |
| `Z*` | campos iniciados em `ztrue_` |

## Escalas psicométricas (`psychometrics.csv`)

- `patient_id` é a chave de junção.
- Itens PHQ-9 e GAD-7 variam de 0 a 3.
- Itens pontuados de IDATE-Estado variam de 1 a 4.
- Totais esperados: `phq9_total` de 0 a 27; `gad7_total` de 0 a 21; `idate_estado_total` de 20 a 80.
- Os totais devem ser derivados dos itens, não gerados independentemente.

## Prioridade (`priority_reference.csv`)

| Campo | Descrição |
|---|---|
| `patient_id` | chave de junção |
| `y_ref` | rótulo ordinal: baixa, moderada, alta, urgente |
| `y_ref_code` | codificação: 0, 1, 2, 3 |
| `urgent_rule_triggered` | indicador de regra determinística de segurança |
| `priority_high_evidence` | soma de evidências de alta prioridade |
| `priority_moderate_evidence` | soma de evidências de prioridade moderada |
| `priority_rule_seed` | semente da etapa de prioridade |

## Marcadores extraídos (`markers_extracted.csv`)

Para cada marcador da ontologia, o extrator produz:

```text
zhat_<marcador>_present
zhat_<marcador>_negated
zhat_<marcador>_temporality
zhat_<marcador>_severity
zhat_<marcador>_severity_code
zhat_<marcador>_certainty
zhat_<marcador>_experiencer
zhat_<marcador>_evidence
```

O campo `_evidence` é textual e não entra nos conjuntos analíticos. Os demais campos podem entrar no conjunto operacional quando forem adequados ao cenário.

## Conjuntos analíticos

Todos possuem as colunas de identificação e alvo:

```text
patient_id, y_ref, y_ref_code, urgent_rule_triggered
```

A seguir, incluem:

- `01_estruturados_escores`: atributos estruturados e totais psicométricos;
- `02_limite_superior_ztrue`: conjunto anterior + `ztrue_*`;
- `03_operacional_zhat`: conjunto estruturado + `zhat_*`, exceto evidência textual.

## Contrato de extensões

Ao adicionar um novo marcador, escala, variável ou modelo:

1. defina seu tipo, faixa, codificação e disponibilidade temporal;
2. atualize geração e validação;
3. atualize os contratos deste documento;
4. atualize a ontologia e os formulários de anotação, quando aplicável;
5. confirme que a informação não viola as fronteiras de `Yref` ou `U`.
