# Regras de não-retenção

Herdadas da `apw-dynamics-copilot`. Valem porque os documentos de site de telecom carregam muita PII: CPF de proprietários, CNPJ, valores de contrato, endereços residenciais.

1. **Nunca** crie arquivos em `/mnt/user-data/outputs/` ou `/home/claude/` com o conteúdo dos contratos, com a PII extraída, ou com o payload do CRM. O processamento é em memória / no contexto da conversa.

2. **Nunca** mande dados do contrato ou do CRM por `web_search`, `image_search` ou qualquer ferramenta externa — nem nome de proprietário, nem "só pra checar uma coisa". Exceção controlada: a geocodificação do passo 3 (nível MÉDIA) precisa de um endereço. Mande **só o endereço do site** (rodovia, km, bairro, município) — nunca o nome, CPF ou dados pessoais do proprietário junto.

3. **Não persista** entre sessões. Cada criação de PIN é stateless. Nada de "vou salvar pra referência futura".

4. **Não use `memory_user_edits`** para gravar conteúdo de deals (códigos de site específicos, nomes de proprietários, valores). Preferências de formato e padrões de uso, tudo bem; conteúdo de contrato, não.

5. Se o Lucas pedir um arquivo final (um resumo do PIN criado, por exemplo), pergunte antes o que pode ir, e persista só o resumo agregado que ele aprovar — nunca o dump bruto do contrato.
