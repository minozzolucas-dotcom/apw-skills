---
name: apw-mytower-acerto
description: >
  Use SEMPRE que o Lucas pedir o acerto de remuneração da MyTower pelos envios de contratos e leads
  — "fecha o acerto da MyTower", "quanto devemos pro Max", "roda o demonstrativo MyTower",
  "pede a NF pro Max", "atualiza a coluna V", "quantos contratos e leads a MyTower mandou",
  "manda o demonstrativo pra MyTower emitir a nota" — ou colar/apontar a planilha
  batch_mytower_controle pedindo consolidação de valores devidos. Acione também quando surgir
  mudança de tabela (valor por contrato ou por lead), dúvida sobre quais sites entram na cobrança,
  ou quando a NF da MyTower chegar. NÃO use para o cruzamento de contratos com o CRM
  (analise-mytower), para pagamento de fornecedor genérico com NF em mãos (apw-vendor-payment),
  nem para wire de closing (apw-request-for-wire).
---

# APW × MyTower — Acerto de Envios

## Overview

A MyTower origina oportunidades para a APW e é remunerada **por envio**: um valor por contrato
enviado e outro por lead enviado. Esta skill fecha o ciclo: contar os envios → produzir o
demonstrativo → pedir a NF → entregar ao contas a pagar.

**Princípio:** o demonstrativo é a fonte da verdade da contagem. Ele existe para que a MyTower emita
uma nota que a APW consiga pagar sem retrabalho — e para que, se a relação azedar, exista um
documento que mostra exatamente o que foi cobrado e por quê.

---

## Fonte de dados

Planilha **`batch_mytower_controle`** (Google Drive, aba principal):

| Coluna | Conteúdo |
|---|---|
| **U** — Valor Devido MyTower | Texto do que foi enviado: `CONTRATO ENVIADO – R$X, LEAD ENVIADO – R$Y` |
| **V** — Total Devido (R$) | Soma por linha — é o campo que se recalcula |
| **W** — Entra no Piloto? | Marcador de escopo |

A coluna U é texto livre e **pode conter a tabela antiga**. Nunca some U diretamente: leia o *tipo*
de envio (contrato / lead / ambos) e aplique a tabela vigente.

---

## Tabela vigente

| Envio | Valor |
|---|---|
| Contrato enviado | **R$ 250,00** |
| Lead enviado | **R$ 50,00** |

Tabela anterior: R$200 / R$30. **Confirme a tabela com o Lucas a cada rodada** antes de calcular —
ela já mudou uma vez e a coluna U guarda o texto antigo.

---

## Quem NÃO entra na cobrança

Três categorias de exclusão. Sempre nomeie o motivo na coluna de observação:

1. **Fora do escopo do piloto** — site marcado como não participante.
2. **Declinado pela APW por causa registral** — ex.: imóvel sem matrícula no RGI. O envio ocorreu,
   mas o acordo comercial não remunera site inviável. **Confirme com o Lucas** se a exclusão é
   pacífica; é o ponto mais provável de discordância da MyTower.
3. **Lead inbound da APW** — originado por Instagram, 0800 ou prospecção própria. Não é MyTower.
   Verifique a origem no CRM antes de excluir.

---

## Entregáveis

### 1. Excel — `Demonstrativo_Envios_MyTower.xlsx`

**Aba "Demonstrativo":** uma linha por site (#, site, cidade/UF, contrato enviado 1/0,
lead enviado 1/0, valor contrato, valor lead, total, observação). Linhas sem cobrança em cinza.
Valores unitários em células de parâmetro no topo, referenciadas por fórmula — assim a troca de
tabela é um único edit. Linha de total com `SUM`.

**Aba "Dados para Faturamento":** prestador, tomador, serviço/valor, pendências.

**Nunca inclua colunas de "valor anterior" ou delta no arquivo que vai para a MyTower.** Serve
para conferência interna; para o fornecedor é ruído e convida a discussão sobre a tabela antiga.

### 2. E-mail para a MyTower

**Para:** max.aureliano@mytower.com.br
**CC:** tiago@mytower.com.br · nf@mytower.com.br · dbueno@apwbrasil.com.br · lalfredo@apwbrasil.com.br

Conteúdo: resumo dos totais, menção às exclusões com motivo, dados do tomador, orientação de
descrição do serviço, convite a apontar divergência **antes** de emitir.

### 3. Handoff

NF recebida → `apw-vendor-payment` monta a solicitação para `contasapagar@apwbrasil.com.br`.

---

## Dados fixos

### Prestador — MyTower

| Campo | Valor |
|---|---|
| Nome empresarial | MYTOWER TECNOLOGIA LTDA |
| CNPJ | 20.535.585/0001-51 (matriz, ATIVA desde 18/04/2023, ME) |
| Endereço **fiscal** | R. Visconde de Parnaíba, 3387 — Apto 71, Bloco A — Brás — São Paulo/SP — 03.045-002 |
| Endereço comercial | Av. Paulista, 807 — Cj. 2315 — Bela Vista — 01311-100 |
| CNAE principal | 62.09-1-00 (suporte/TI) |
| CNAEs secundários | 63.19-4-00 · 82.19-9-99 · 73.12-2-00 · 73.19-0-99 · 82.91-1-00 |
| E-mail de NF | nf@mytower.com.br |
| Rep. legal | Tiago Calimério Albino (Founder & CEO) |
| Comercial | Max Medeiros Aureliano de Lima |
| **PIX (preferencial)** | 20.535.585/0001-51 (CNPJ) |
| TED | Banco PagSeguro (cód. 290) · Ag. 0001 · C/C 0205782-7 |

### Tomador — APW

AP WIRELESS BRASIL INVESTIMENTOS IMOBILIÁRIOS LTDA. · IM 4.475.921-5 ·
Alameda Santos, 2477 — Conj. 0071, 7º andar — Cerqueira César — São Paulo/SP — 01419-101

⚠️ **CNPJ ambíguo.** A assinatura de e-mail do Lucas traz `15.090.468/0001-91`; o cadastro interno
registra `15.090.397/0001-27`. **Pergunte ao Lucas a cada rodada.** NF emitida contra o CNPJ errado
volta e trava o pagamento.

---

## A armadilha do CNAE

A MyTower **não tem CNAE de intermediação ou corretagem imobiliária (68.22-6-00)**. Uma nota
descrita como "intermediação de negócios" ou "corretagem" documenta um serviço que o prestador não
está registrado para prestar — e corretagem imobiliária ainda esbarra em CRECI. A APW estaria
pagando uma NF viciada.

**Descrição a usar:**
> Serviços de informação e apoio administrativo — disponibilização de dados cadastrais e
> documentação de imóveis para infraestrutura de telecomunicações.

Casa com 63.19-4-00 / 82.19-9-99 / 82.91-1-00. O código da LC 116/2003 é decisão do contador da
MyTower — oriente a descrição, não o enquadramento.

---

## Erros comuns

| Erro | Consequência |
|---|---|
| Somar a coluna U literalmente | Usa a tabela antiga e subfatura |
| Cobrar contrato **e** lead em todo site | Alguns tiveram só contrato. Leia U linha a linha |
| Mandar o endereço da Av. Paulista para a NF | Endereço fiscal é o do Brás |
| Deixar delta/comparação no arquivo do fornecedor | Abre discussão sobre a tabela anterior |
| Inventar CNPJ, banco ou inscrição municipal | Pagamento vai para o lugar errado |
| Pedir CCM ao Max | Sai impressa na própria NFS-e |
| Pedir dados bancários já cadastrados | Passa desorganização em relação de piloto |

**Nunca preencha CNPJ, dados bancários, número de NF ou vencimento por dedução.** Se não estiver em
documento à mão, o campo fica amarelo e vai para a lista de pendências.

---

## Checklist

- [ ] Tabela vigente confirmada com o Lucas
- [ ] Coluna U lida linha a linha (contrato / lead / ambos)
- [ ] Exclusões classificadas e justificadas
- [ ] Total confere com a soma manual dos unitários
- [ ] Excel sem colunas de comparação
- [ ] CNPJ do tomador confirmado
- [ ] Descrição do serviço aderente ao CNAE
- [ ] E-mail com CC para nf@mytower.com.br, Diogo e Luiz Alfredo

---

## Nota de manutenção

Skill escrita a partir de uma rodada real de acerto, sem a fase RED de teste com subagente prevista
em `writing-skills`. Trate a primeira execução como validação: divergências encontradas devem virar
linha na tabela de erros comuns.
