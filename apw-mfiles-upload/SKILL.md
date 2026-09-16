---
name: apw-mfiles-upload
description: Use quando o Lucas pedir para SUBIR / ARQUIVAR documentos de um deal no M-Files via agente de navegador — "sobe os docs no M-Files", "arquiva no M-Files do Lxxxx", "faz upload no M-Files", "joga esses arquivos no M-Files", "guarda no M-Files". A skill usa o Claude in Chrome para enviar os arquivos do deal ao M-Files (mfilesus.apwip.com), classificando cada um com a CLASSE (Categoria) e o nome padronizado da APW e relacionando ao L-number — sempre com confirmação do Lucas antes do check-in. NÃO use para LER o conteúdo de PDF do M-Files (peça o anexo no chat), para a pré-DD/análise registral (apw-pre-dd-legal), nem para gravar no Dynamics/CRM (apw-crm-key-notes-writer).
---

# APW M-Files Upload — Arquivamento de docs do deal via agente

## Overview
Sobe os documentos de um deal ao **M-Files** (`mfilesus.apwip.com`) usando o **Claude in Chrome**, **um arquivo por vez**, **classificando** cada peça com a **Categoria (classe M-Files)** e o **nome padronizado** da APW e **relacionando ao L-number**. M-Files é orientado a metadados: subir um arquivo é criar um objeto com **classe + propriedades + relação ao deal** e depois fazer **check-in** (commit). Princípio inegociável: o agente **prepara e mostra**; o **check-in só acontece com o OK do Lucas**.

## When to use
- "sobe os docs no M-Files", "arquiva no M-Files do Lxxxx", "faz upload no M-Files", "guarda esses arquivos no M-Files".

**Não usar para:** LER conteúdo de PDF do M-Files (o visualizador não expõe o texto — pedir o anexo no chat); pré-DD / análise registral (`apw-pre-dd-legal`); gravar no Dynamics/CRM (`apw-crm-key-notes-writer`).

## Regras inegociáveis — M-Files é sistema de registro
Erro aqui suja a fonte da verdade do deal. O agente:
1. **NÃO faz check-in sem o OK do Lucas.** Antes de commitar, **MOSTRA o mapeamento** (arquivo → classe → nome → L-number → propriedades) e **espera confirmação**. Check-in é o commit irreversível.
2. **NÃO sobrescreve / não cria nova versão** de documento existente. Se já há peça com a mesma classe/nome no deal → **PARA e pergunta**.
3. **NÃO deleta nada, não altera permissões/compartilhamento, não mexe em outras propriedades** do objeto do deal.
4. **NÃO faz login/MFA.** Tela de autenticação → **PARA**, o Lucas autentica.
5. **Um arquivo por vez**, confirmando que a **relação é com o L-number certo** antes de cada check-in.
6. Domínio corporativo (`*.apwip.com`) → seguir `apw-chrome-agent-lean-compliance`: `read_page` / `get_page_text` / `javascript_tool` **antes** de qualquer screenshot; evitar screenshot de dados sensíveis.
7. Os arquivos precisam estar **no computador do Lucas** (o Chrome só sobe do filesystem local, via `file_upload`) — baixar os outputs do chat antes.

## Inputs (coletar antes de subir)
- **L-number** do deal.
- **Lista de arquivos** a subir (caminhos locais no PC do Lucas).
- Para cada arquivo: a **Categoria (classe)** e o **nome padronizado** — usar a tabela abaixo. Arquivo que não casar → **perguntar**, não inventar.

## Mapa de classificação (classe M-Files + nome padronizado APW)
Espelha a planilha de diligência da APW (colunas *Categoria* + *Custom Name*).

| Documento | Categoria (classe M-Files) | Nome padronizado |
|---|---|---|
| Carta de Intenção assinada | (F)Signed Offer Agreement | 01. Carta de Intenção |
| Contrato de Locação (operadora/torreira) | (F)Lease | 02. Contrato [Operadora] |
| Termo Aditivo ao Contrato | (F)Amendment | 03. Termo Aditivo [Operadora] (Nº) |
| Certidão de Registro Civil (nasc./casamento) | Unclassified Document | 04. Certidão de Nascimento / Casamento |
| RG e CPF do(s) proprietário(s) | Unclassified Document | 05. RG e CPF |
| Comprovante de Residência / estado civil / profissão | Unclassified Document | 06. Comprovante de Residência |
| Espelho do IPTU / dados cadastrais | Unclassified Document | 07. Espelho do IPTU |
| Certidão da Matrícula (c/ ônus / alienações) | Unclassified Document | 08. Certidão da Matrícula |
| CND de IPTU / débitos imobiliários | Unclassified Document | 09. CND - IPTU |
| Comprovante dos 3 últimos aluguéis (POP) | (F)Proof of Payment | 10. Comprovante Pagamento |
| Fotos da torre / equipamentos | Site Photos | 11. Fotos |
| Escritura / certidões da PF / saldo de quitação / outros | Unclassified Document | NN. [descrever] |

Classe ou nome em dúvida → **perguntar**. Classe errada quebra a busca por categoria na DD.

## Procedimento (por arquivo)
1. Abrir `mfilesus.apwip.com`. Se pedir login/MFA → **PARA** (Lucas autentica).
2. Buscar o **L-number**; abrir o **objeto/projeto do deal**.
3. **New > Document** (ou "Add file"): selecionar a **classe** (Categoria) e anexar o arquivo via `file_upload`.
4. Definir o **nome** (padrão da tabela) e **relacionar ao L-number** (propriedade de relação ao deal).
5. Preencher as **propriedades obrigatórias** que o M-Files exigir. Campo obrigatório ambíguo → **PARA e pergunta**.
6. **MOSTRAR o mapeamento** (arquivo → classe → nome → L-number → props) e **esperar o OK**.
7. Só então **check-in**. Verificar que o documento aparece no deal. Reportar.

## Consolidação (output)
Tabela **arquivo → classe → nome → status**, com `status ∈ {SUBIDO, AGUARDA-CONFIRMAÇÃO, JÁ EXISTE, LOGIN, FALHOU}`. Listar separadamente: o que subiu, o que parou (e por quê), o que ficou de fora.

## Rationalization table
| Desculpa | Realidade |
|---|---|
| "Já confirmei mentalmente, faço o check-in" | Check-in **só** com OK explícito do Lucas. |
| "O doc parece o mesmo, crio nova versão" | Não versionar/sobrescrever. PARA e pergunta. |
| "Falta uma propriedade, invento um valor" | Campo obrigatório ambíguo → PARA. Não inventar metadado. |
| "A classe mais próxima serve" | Classe errada suja a busca da DD. Em dúvida, perguntar. |
| "Loga rapidinho pra agilizar" | Não logar. Lucas autentica. |

## Red flags — PARE
Tela de login/MFA · documento já existente com mesma classe/nome · campo obrigatório sem valor claro · pedido para alterar permissão / excluir / mover outro objeto · relação de deal divergente do L-number. → **PARA**, marca o status, devolve ao Lucas.

## Common mistakes
- Subir sem **relacionar ao L-number** (documento órfão).
- **Classe errada** (quebra a busca por categoria na DD).
- **Check-in em lote** sem conferência (commit de metadado errado).
- Tentar **ler o PDF** pelo M-Files (o visualizador não expõe o texto — pedir o anexo no chat).

## Quick reference
| Sintoma | O que fazer |
|---|---|
| "sobe no M-Files" | Rodar: um arquivo por vez, classe+nome padrão, relacionar ao L-number, **confirmar**, check-in. |
| Doc já existe no deal | PARA — não versiona/sobrescreve. Pergunta. |
| Tela de login/MFA | PARA — Lucas autentica. |
| Classe/nome em dúvida | Perguntar — não inventar metadado. |
| Pediram pra LER PDF do M-Files | Não dá pelo visualizador — pedir o anexo no chat. |
