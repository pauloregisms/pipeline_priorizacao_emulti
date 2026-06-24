## Resumo

Descreva objetivamente a mudança e o problema que ela resolve.

## Tipo de alteração

- [ ] Correção de erro
- [ ] Nova funcionalidade
- [ ] Alteração de parâmetro ou cenário de simulação
- [ ] Mudança metodológica ou de arquitetura
- [ ] Documentação
- [ ] Refatoração sem alteração de comportamento esperado

## Segurança e integridade metodológica

- [ ] Não incluí dados reais, identificáveis ou sensíveis.
- [ ] Não incluí credenciais, tokens ou arquivos `.env`.
- [ ] A alteração não envia `Yref`, prioridade, códigos ou limiares ao gerador de narrativas.
- [ ] A alteração preserva a separação entre `Z*`, `Zhat` e variáveis de auditoria.
- [ ] Não interpretei resultados sintéticos como evidência clínica.

## Validação executada

Inclua comandos e resultado resumido.

```text
python -m compileall src scripts
python scripts/run_pipeline.py ...
```

## Documentação atualizada

- [ ] README atualizado quando necessário.
- [ ] Documento em `docs/` atualizado.
- [ ] `CHANGELOG.md` atualizado quando a mudança for relevante para usuários.
- [ ] ADR criado ou atualizado quando a decisão for arquitetural/metodológica.

## Impacto esperado

Descreva impactos em contratos de dados, artefatos, parâmetros, modelos, métricas ou reprodutibilidade.
