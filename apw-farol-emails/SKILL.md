---
name: apw-farol-emails
description: Rotina do Lucas para sincronizar os emails de closing dos 16 deals APW no Farol de Closing — puxa do Gmail pessoal (minozzo.lucas@gmail.com) os emails encaminhados pela regra "Farol APW → Gmail" do Outlook corporativo (from lminozzo@radiusglobal.com com L# no assunto/corpo), resume cada thread por deal, e gera um updates-comms.json pronto para importar no farol (farol-closing-apw.pages.dev). Use SEMPRE que o Lucas disser "puxa os emails do farol", "sincroniza o farol", "atualiza as comunicações do farol", "roda o farol de emails", "atualiza o farol", "traz o que aconteceu nos deals essa semana", ou variação pedindo consolidar comunicações de closing por deal. Trigger também ao mencionar "emails do farol", "log de comunicações do farol", "aba Detalhes do farol", ou depois de call semanal de closing pedindo o que rolou por email. NÃO use para dossiê de UM deal (apw-deal-dossier), forensics de atividades (apw-opp-activity-forensics), briefing de reunião (apw-meeting-brief), nem para editar o próprio HTML do farol.
---

# apw-farol-emails

Consolida em uma única passada os emails de closing dos deals ativos do Farol e devolve um arquivo updates-comms.json pronto para o botão Importar do farol.

## Contexto fixo (não perguntar ao Lucas)

- Gmail que Claude lê: minozzo.lucas@gmail.com (conector Gmail ativo)
- Remetente esperado no Gmail: lminozzo@radiusglobal.com (Lucas encaminhando via regra Outlook "Farol APW → Gmail")
- Farol no ar: https://farol-closing-apw.pages.dev
- Deals ativos no farol (16 L#): L959023, L924554, L362835, L1067615, L923086, L921623, L980570, L1108371, L921683, L1357080, L1357192, L1068138, L884789, L942661, L1261983, L1275179, L980793
- Janela default: últimos 7 dias

## Passo 1 — buscar no Gmail

Use mcp__Gmail__search_threads com a query:

from:lminozzo@radiusglobal.com (L959023 OR L924554 OR L362835 OR L1067615 OR L923086 OR L921623 OR L980570 OR L1108371 OR L921683 OR L1357080 OR L1357192 OR L1068138 OR L884789 OR L942661 OR L1261983 OR L1275179) newer_than:7d

- pageSize: 50. Se vier 50, paginar.
- Substituir newer_than:7d pela janela pedida.
- Vazio → avisar "nada novo em X dias" e parar.

## Passo 2 — extrair conteúdo

Para cada thread:
1. Usar snippet se suficiente.
2. mcp__Gmail__get_message com messageFormat: PLAIN_TEXT se ambíguo.
3. Extrair:
   - L# de destino (regex L\d{5,7}; múltiplos = uma entrada em cada deal)
   - Remetente ORIGINAL (procurar "De:" ou "From:" no corpo — não confundir com lminozzo@radiusglobal.com que é sempre o encaminhador)
   - Data ORIGINAL (do email de origem, não a data do encaminhamento)
   - Assunto limpo (sem ENC:, FW:, RES:, RE:)
   - Resumo curto (1-2 frases, pt-BR, denso — objetivo: bater olho e saber status)

## Passo 3 — montar updates-comms.json

Formato exato que o farol dedupe por date+subject+source:

{
  "updates": [
    {
      "code": "L959023",
      "log": [
        {
          "date": "2026-09-25",
          "source": "Email",
          "subject": "Assunto limpo",
          "from": "Nome <email@dominio>",
          "summary": "1-2 frases pt-BR"
        }
      ]
    }
  ]
}

Regras:
- code em MAIÚSCULA sempre (L959023, não l959023).
- date = data do email ORIGINAL, YYYY-MM-DD.
- source = "Email" (ou "Teams" se for reencaminhamento de mensagem Teams via Share to Outlook).
- Uma entrada por email. Email mencionando 2 L# = duas entradas (uma em cada code).
- Múltiplos emails do mesmo deal = múltiplas entradas dentro do log daquele code.

## Passo 4 — salvar e apresentar

1. create_file em /mnt/user-data/outputs/updates-comms.json.
2. present_files só do JSON.
3. Resumo ANTES do card: quantos emails, quantos deals, bullet por deal com contagem e 1ª linha do mais recente.
4. Fechar com: "Importa no farol pra atualizar a aba Detalhes de cada deal."
5. Nunca abrir o farol ou tentar importar sozinho — o Lucas importa manual.

## Casos-limite

- "Desde sempre" → after:2026/09/25 (dia que a regra Outlook entrou no ar).
- Thread grande → só a msg mais recente da thread.
- Deal fora dos 16 → incluir + avisar "Achei L##### que não está no farol — adicionar?".
- Email com anexo → mencionar no summary: "[com anexo: xxx.pdf]".
- Bounce/OOO/auto → filtrar fora, não gera log.

## O que NÃO fazer

- JSON vazio → só texto explicando que não achou nada.
- Perguntar coisas que a skill já sabe (Gmail, remetente, formato, lista dos 16 L#).
- Mostrar o JSON inteiro no chat — vai no arquivo.
- Misturar deals num único code.
- Modificar o farol (HTML/deploy).
