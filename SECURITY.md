# Segurança, dados e comunicação responsável

## Escopo de dados permitido

Este repositório foi projetado para trabalhar exclusivamente com **dados sintéticos**. É proibido inserir, anexar, versionar, registrar em log ou enviar a um provedor externo:

- prontuários ou trechos de prontuários;
- nomes, endereços, telefones, documentos, identificadores de pacientes ou profissionais;
- qualquer informação pessoal, sensível ou potencialmente identificável;
- chaves de API, tokens, senhas, certificados ou arquivos `.env` reais.

## Credenciais de APIs futuras

A versão atual não chama serviços externos. Caso um adaptador de LLM seja implementado no futuro:

- armazene credenciais apenas em variáveis de ambiente, cofre de segredos ou configuração local ignorada pelo Git;
- nunca grave credenciais em YAML, notebooks compartilhados, artefatos ou logs;
- use privilégios mínimos e rotação de chaves quando o serviço permitir;
- registre metadados do modelo e da execução, mas não conteúdo sensível;
- confirme que as políticas do provedor são compatíveis com o uso exclusivamente sintético do projeto.

Um arquivo `.env.example` pode documentar nomes de variáveis sem conter valores reais.

## Relato de vulnerabilidades

Não publique detalhes de vulnerabilidades, exposição de credenciais ou inclusão acidental de dados no rastreador público de issues. Entre em contato com o responsável pelo repositório por canal privado e inclua:

- descrição do problema;
- arquivos ou componentes envolvidos;
- impacto potencial;
- passos mínimos para reprodução;
- evidências de que nenhum dado sensível foi compartilhado na comunicação.

## Salvaguarda metodológica

Uma falha de segurança também pode ser metodológica. São consideradas críticas as alterações que:

- enviem `Yref` ou pistas equivalentes ao gerador de narrativas;
- misturem `Z*` e `Zhat` sem declaração explícita;
- introduzam variáveis de auditoria, como `u_latent_audit_only`, nos classificadores;
- permitam execução com dados reais sem uma avaliação ética e institucional independente.
