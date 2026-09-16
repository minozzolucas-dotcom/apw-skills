---
name: apw-dossie-cessao
description: Gera o DOSSIÊ INFORMATIVO de Cessão de Direitos Creditórios (CDC) da APW Brasil — PDF de 2 páginas na marca oficial explicando ao condomínio como a operação funciona, os números da receita da antena, a estrutura da antecipação à vista e o tratamento fiscal (Lei 12.973/2014, não-distribuição, ausência de personalidade jurídica). Antes de gerar, COLETA as informações necessárias via checklist. Use SEMPRE que o Lucas pedir "dossiê da cessão", "material informativo pro condomínio", "doc de cessão", "material explicativo CDC", "guideline cessão pro síndico", "monta o material do condomínio [nome]", ou mandar aluguel mensal + nº de unidades pedindo o material. NÃO use para a proposta comercial com valores e TIR (apw-proposta-comercial), parecer de cláusula (apw-telecom-real-estate-counsel), material de DRS/terreno PF (apw-dossie-drs), nem negociação de redline (apw-negociacao-contrato).
---

# APW Dossiê Informativo — Cessão de Direitos Creditórios

Gera o material educativo/informativo em PDF (marca APW) que os diretores de aquisição enviam a síndicos e condôminos para explicar a operação de cessão de recebíveis da antena. **Não é a proposta comercial** — é o material de suporte que responde "como funciona e qual o tratamento fiscal".

## Passo 1 — Coleta de informações (checklist obrigatório)

Antes de gerar qualquer coisa, verifique quais inputs já estão na conversa e **pergunte só o que faltar**, numa única mensagem compacta:

**Obrigatórios:**
1. **Aluguel mensal atual da antena** (R$)
2. **Número de unidades** do condomínio
3. **Valor da antecipação à vista** proposto (se ainda não definido, usar placeholder `R$ [valor]` e avisar)
4. **Prazo da cessão** (anos — default 30 se o Lucas não disser)

**Opcionais (melhoram o material):**
5. Nome do condomínio (senão: `[Nome do Condomínio]`)
6. Operadora/torreira pagadora (ATC, SBA, TIM, Vivo...)
7. Código L do deal
8. Condomínio **residencial ou comercial** — ver guardrail abaixo
9. Destino pretendido do recurso (obras, fundo de reserva...)
10. Histórico de distribuição da receita aos condôminos (default: nunca distribuiu — confirmar, pois é pilar do argumento fiscal)

## Passo 2 — Cálculos

- Receita anual = aluguel mensal × 12
- Valor anual por unidade = receita anual ÷ nº de unidades
- Formatar tudo em R$ padrão brasileiro (ponto de milhar, vírgula decimal)

## Passo 3 — Gerar o PDF

Use o template `assets/template_cessao.html` (estrutura e CSS já validados na marca APW: navy #012B5E, azul #1C75BB, sage #91A5A4, Arial, wordmark em texto). Substitua os valores do exemplo pelos do deal e renderize:

```bash
pip install weasyprint --break-system-packages -q
python -c "from weasyprint import HTML; HTML('doc.html').write_pdf('/mnt/user-data/outputs/APW_Brasil_Cessao_[Condominio].pdf')"
```

Estrutura fixa do documento (5 seções + disclaimer):
1. Receita e depósito — cenário atual
2. Receita atual em números (4 cards KPI: mensal, anual, por unidade, antecipação)
3. Proposta de cessão de direitos (box verde "Estrutura da operação")
4. Tratamento fiscal — fundamentos e perfil do condomínio (4 bullets + tabela de referências)
5. Conclusão (curta, sem box de alerta)

## Guardrails fiscais — NÃO NEGOCIÁVEIS

Leia `references/base_fiscal.md` antes de alterar qualquer texto da seção fiscal. Regras duras:

1. **NUNCA escrever afirmação categórica** do tipo "a operação não é alvo da Receita Federal" ou "não há imposto devido". A seção fiscal conduz o leitor pela lógica (sem personalidade jurídica → não é contribuinte; Lei 12.973/14 elegeu a distribuição como divisor de águas; perfil de não-distribuição = menor exposição; pós-cessão o fluxo vira receita da APW) **sem fechar a tese por escrito**. Motivo: ADI SRF 2/2007 e SD Cosit 3/2007 atribuem o rendimento aos condôminos mesmo sem distribuição, e a isenção da 12.973/14 tem teto de R$ 24.000/ano — quase todo deal APW está acima. Afirmação absoluta vira munição contra a APW na mão do contador da contraparte.
2. A isenção da Lei 12.973/14 vale só para condomínio **residencial** (Lei 4.591/64). Se o condomínio for comercial, remover a menção à isenção e apoiar a seção apenas na ausência de personalidade jurídica + divisor da distribuição + efeito da cessão.
3. O disclaimer final ("não se trata de parecer contábil ou jurídico...") é obrigatório e não pode ser removido, mesmo que pedido — nesse caso, avisar o Lucas do risco e só remover com confirmação explícita dele.
4. Se o Lucas pedir a frase categórica mesmo assim, gerar somente após alertar uma vez e recomendar validação com o jurídico (Michelle/Anderson).

## Passo 4 — Entrega

`present_files` com o PDF + resumo de 3-4 linhas do que foi personalizado e o que ficou como placeholder.
