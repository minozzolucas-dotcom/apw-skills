---
name: apw-brand
description: >
  Fonte única da identidade visual e verbal da APW Brasil (APWireless Brasil). Use SEMPRE
  que qualquer deliverable APW precisar de marca — reporte, proposta, e-mail, deck, dashboard,
  documento, PNG — para aplicar paleta, tipografia, logo, razão social e regras de e-mail
  oficiais. Carregue esta skill junto das demais skills apw-* (reporte-crm-diario,
  proposta-comercial, counterparty-assessment, analise-mytower etc.) para garantir cor e
  tipografia idênticas em tudo. Acione com "identidade APW", "cor da APW", "deixa na marca",
  "padrão visual APW", "brand APW", ou quando notar divergência de cor entre materiais.
---

# APW Brasil — Brand Kit

Identidade canônica da APW Brasil. Resolve a divergência histórica de cores entre skills
(houve `#012B5E`, depois `#1F3668` extraído de PNG, e a reversão para a paleta oficial).
**Esta é a paleta oficial — use só ela.**

## Paleta (Brand Guidelines)

| Token | Hex | Uso |
|---|---|---|
| Navy | `#012B5E` | Institucional: capas, cabeçalho/rodapé cheios, header de tabela, títulos |
| Azul APW | `#1C75BB` | Acento principal: filetes, links, barras, "APW" do wordmark, destaques |
| Sage | `#91A5A4` | Secundário: rótulos auxiliares, o "Brasil" do wordmark, legendas |
| Verde | `#009877` | Positivo / meta batida |
| Oliva | `#A7AF00` | Atenção / atrás da meta. **Nunca usar âmbar/laranja off-brand.** |
| Cinza | `#5D5D5D` | Texto de apoio |
| Branco / Preto | `#FFFFFF` / `#000` | Conforme necessário |

Auxiliares de fundo claro: `#f4f7fa`, `#eef2f6`, `#dbe4ee`, `#FBFBEF` (caixa oliva).

## Tipografia

**Arial** em tudo (fonte oficial APW para mídia digital e e-blasts). Sem fontes externas.

## Logo

- Sistema oficial: Logomark (hexágono sage com triângulo azul), Abreviado (logomark + "APW"), Vertical.
- Regra dura: **nunca** alterar/recriar o logo, nunca improvisar o hexágono em SVG, sempre preservar proporção, nunca pílula branca.
- Em material renderizado (PDF/deck/PNG): usar o **PNG oficial** (logo_apw_brasil.png — manter cópia em `assets/`; hoje também existe em `apw-proposta-comercial/assets/`).
- Em **e-mail**: usar **wordmark em texto** — `APW` (branco ou navy) + `Brasil` (sage), Arial bold — NÃO embutir logo (Outlook desktop quebra base64 e não renderiza SVG).

## Wordmark em texto

`<span style="font-weight:bold;color:#012B5E">APW</span><span style="color:#91A5A4">Brasil</span>`
(em fundo navy, trocar o "APW" para `#fff`.)

## Razão social (rodapé)

**APWireless Brasil Invest. Imob. LTDA**

## Regras de e-mail (aprendido na prática)

- O Outlook, ao **colar HTML**, preserva fundos/bordas mas **zera a cor do texto** (vira tudo preto). 
- **Solução padrão: entregar como PNG** (renderizar o HTML com Chrome headless e colar a imagem). Mantém a marca 100%.
- Se precisar de HTML editável no corpo: usar layout **texto escuro sobre fundo claro** (navy sobre branco), nunca depender de texto branco/claro — assim, faça o Outlook o que fizer com a cor, continua legível. Tudo inline-CSS, layout em `<table>`, sem SVG.

## Voz

Direta, factual, sem adjetivação vazia em materiais internos/executivos. Bilíngue PT/EN conforme público (Brasil = PT; IC/San Diego = EN).

### Tratamento — REGRA DURA (vale para TODA skill apw-*)

Em QUALQUER deliverable que fale com uma contraparte externa — cedente, proprietário, síndico, condomínio, advogado da outra parte, torreira, operadora — o tratamento é **"você"**, nunca **"o senhor / a senhora"**.

A APW são **diretores de aquisição**; a conversa é **de igual para igual com o decisor**, com autoridade tranquila. "O senhor" lê como vendedor pedindo licença — submissão — e enfraquece a posição. Está **proibido** em propostas, e-mails, dossiês para cliente, cartas, materiais informativos (Cessão/DRS) e qualquer peça de negociação.

- ✅ "Você continua dono do terreno", "como você conhece o setor", "o valor fica disponível para você".
- ❌ "O senhor continua dono", "como o senhor sabe", "à disposição do senhor".
- Formalidade se faz com **precisão e substância**, não com pronome de subserviência. Trate o interlocutor como par competente.
- Vale mesmo quando o cedente é PF idosa ou "sofisticada": o registro é de par, não de deferência.
- **Exceção única:** se o próprio Lucas pedir explicitamente "trata por senhor neste caso" (ex.: exigência cultural de um cedente específico), aí sim — mas o default é sempre "você".
- Em EN (IC/San Diego), o equivalente já é natural ("you"); a regra é sobre o PT.
