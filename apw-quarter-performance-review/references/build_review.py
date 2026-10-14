#!/usr/bin/env python3
"""build_review.py — APW Quarter Performance Review
Gera reviews individuais + consolidado do time pra UKG.

Uso:
  python3 references/build_review.py \
    --harvest=harvest.json --rent-pbi=data/rent_pbi_oficial.csv \
    --inputs=inputs/ --periodo=9M-2026 --out=out/
"""
import sys, json, csv, os, re, html as _h
from pathlib import Path
from datetime import date
from collections import defaultdict

NAVY="#012B5E"; AZUL="#1C75BB"; SAGE="#91A5A4"; VERDE="#009877"; OLIVA="#A7AF00"
RED="#C0392B"; CINZA="#5D5D5D"; AMBAR="#E8A33D"; BG2="#f7fafc"; LINE="#dce4ec"

ESCALA_UKG = {
    4: "Exceptional",
    3: "Exceeds Expectations",
    2: "Meets Expectations",
    1: "Needs Improvement / Below Expectations"
}
COR_NOTA = {4: VERDE, 3: OLIVA, 2: AZUL, 1: RED}

PERIODOS = {
    "H1-2026":  {"meses_ini":1,"meses_fim":6,  "fator":0.5,  "label":"H1 2026 (jan-jun)"},
    "9M-2026":  {"meses_ini":1,"meses_fim":9,  "fator":0.75, "label":"9M 2026 (jan-set)"},
    "Q3-2026":  {"meses_ini":7,"meses_fim":9,  "fator":0.25, "label":"Q3 2026 (jul-set)"},
    "H2-2026":  {"meses_ini":7,"meses_fim":12, "fator":0.5,  "label":"H2 2026 (jul-dez)"},
    "FY-2026":  {"meses_ini":1,"meses_fim":12, "fator":1.0,  "label":"FY 2026 (ano todo)"},
}

PESOS = {1: 30, 2: 20, 3: 15, 4: 15, 5: 5, 6: 5, 7: 5}
PESO_TOTAL = sum(PESOS.values())  # 95

META_REGIME = {
    "Sr Experiente":      {"s1":100, "s3":60, "s8":12, "s99":10},
    "Novo+Pleno":         {"s1":140, "s3":70, "s8":10, "s99":8},
    "Novo+Pleno-novo":    {"s1":140, "s3":70, "s8":10, "s99":8},
    "Novo+Pleno-prorata": {"s1":58,  "s3":29, "s8":4,  "s99":3},  # Marcia 5/12
}

# hire dates pra pro-rata individual quando aplicável
HIRE = {
    "Victoria Navarro":  date(2023,2,6),
    "Gisele Tognolo":    date(2023,9,22),
    "Daiane dos Santos": date(2023,8,11),
    "Carolina Brentzel": date(2024,7,24),
    "Aline Sanzi":       date(2023,5,16),
    "Aline Felix":       date(2025,12,12),
    "Andressa Bueno":    date(2024,11,8),
    "Kamilla Rosa":      date(2023,8,16),
    "Regina Silveira":   date(2023,5,26),
    "Roana Reboredo":    date(2024,12,26),
    "Fabio Boturao":     date(2019,4,23),
    "Felipe Porto":      date(2019,9,26),
    "Jose Daniel Ramos": date(2014,5,15),
    "Marcia Mangiulli":  date(2026,7,28),
}

def esc(t): return _h.escape(str(t or "").strip())
def slug(nome): return re.sub(r"[^a-z]+","-", nome.lower()).strip("-")

def arg(name, default=None):
    pref = f"--{name}="
    for a in sys.argv[1:]:
        if a.startswith(pref): return a[len(pref):]
    return default

def nota_quant(pct):
    if pct >= 110: return 4
    if pct >= 90:  return 3
    if pct >= 70:  return 2
    return 1

def parse_autoaval(path):
    """Parse markdown de autoavaliação em dict {1: {nota, comentario}, ...}"""
    if not Path(path).exists(): return {}
    txt = Path(path).read_text()
    metas = {}
    cur = None
    for linha in txt.splitlines():
        m = re.match(r"##\s+Meta\s+(\d+)", linha)
        if m:
            cur = int(m.group(1))
            metas[cur] = {"nota_texto":"", "nota_num":None, "comentario":""}
            continue
        if cur:
            if linha.startswith("Nota:"):
                nt = linha.split(":",1)[1].strip()
                metas[cur]["nota_texto"] = nt
                nt_low = nt.lower()
                if "exceptional" in nt_low: metas[cur]["nota_num"] = 4
                elif "exceed" in nt_low: metas[cur]["nota_num"] = 3
                elif "meet" in nt_low: metas[cur]["nota_num"] = 2
                elif "needs" in nt_low or "below" in nt_low: metas[cur]["nota_num"] = 1
            elif linha.startswith("Comentario:"):
                metas[cur]["comentario"] = linha.split(":",1)[1].strip()
    return metas

def nota_qualitativa(autoaval_nota, autoaval_comentario, sinais_crm=None, nome_meta=""):
    """Decide nota qualitativa (metas 3,4,5,6) baseado em autoaval + sinais"""
    if not autoaval_nota:
        return 2, "Default Meets (autoavaliação não preenchida)"
    base = autoaval_nota
    just = f"Autoaval: {ESCALA_UKG[base]}"

    if autoaval_comentario:
        c = autoaval_comentario.lower()
        # ORDEM IMPORTA: primeiro checa negação explícita (puxa pra baixo)
        tem_negacao = any(n in c for n in ["não cita","nao cita","não menciona","nao menciona",
                                            "sem evidência","sem evidencia","não detalha","nao detalha",
                                            "genérico","generico","vago","superficial"])
        if tem_negacao and base == 2:
            return 1, just + " mas comentário sem evidência concreta → Needs Improvement"
        # só depois checa evidência positiva (puxa pra cima)
        tem_curso = any(k in c for k in ["udemy","curso","certifica","trilha","workshop","treinamento"])
        tem_iniciativa = any(k in c for k in ["criei","montei","liderei","lider","propus","implementei","mentorei"])
        if not tem_negacao and base == 2 and (tem_curso or tem_iniciativa):
            return 3, just + " + evidência concreta → Exceeds"
    return base, just

def gerar_comentario_quant(nota, meta_label, real, meta_prorata, pct, extras=""):
    comentarios = {
        4: f"Entrega excepcional em {meta_label}: {real} vs meta pro-rata {meta_prorata} ({pct:.0f}%). {extras}Superou com consistência.",
        3: f"Desempenho acima do esperado em {meta_label}: {real}/{meta_prorata} ({pct:.0f}%). {extras}Entregas claramente acima do exigido.",
        2: f"Atingiu com consistência em {meta_label}: {real}/{meta_prorata} ({pct:.0f}%). {extras}Entrega confiável, dentro do esperado.",
        1: f"Abaixo do esperado em {meta_label}: {real}/{meta_prorata} ({pct:.0f}%). {extras}Necessário mudança de ritmo pra atingir meta anual."
    }
    return comentarios[nota]

def monta_metricas(harvest, rent_csv, periodo):
    """Para cada diretor: realizado, meta pro-rata, pct, nota quant das metas 1 e 2"""
    P = PERIODOS[periodo]
    fator = P["fator"]
    rent = {r["diretor"]: r for r in csv.DictReader(open(rent_csv))}

    diretores = []
    for nome in HIRE:
        r_rent = rent.get(nome, {})
        regime = r_rent.get("regime", "Novo+Pleno")

        # ─── Marcia: só qualitativa, sem notas quantitativas (ciclo não aplica) ───
        if nome == "Marcia Mangiulli":
            diretores.append({
                "nome": nome, "slug": slug(nome), "regime": regime,
                "excluir_quant": True, "nota_overall_quant": None,
                "meta": {}, "real": {}, "pct": {},
                "rent_meta": 0, "rent_real": int(r_rent.get("acquired_ytd_brl",0)),
                "rent_pct": 0, "nota_pipeline": None, "nota_business": None
            })
            continue

        meta_base = META_REGIME.get(regime, META_REGIME["Novo+Pleno"])
        # Aline Felix: pro-rata de hire date (dez/2025) → ano cheio é 2026
        # já com 10m de casa no final de set, considera meta integral pro ciclo
        meta_prorata = {k: int(round(v * fator)) for k,v in meta_base.items()}

        # realizado no período
        real = {"s1":0,"s3":0,"s8":0,"s99":0}
        for s in real:
            for r in harvest["stages"].get(s, []):
                if r["ownerName"] == nome and r["year"] == 2026 and \
                   P["meses_ini"] <= r["month"] <= P["meses_fim"]:
                    real[s] += r["count"]

        pct = {s: (100*real[s]/meta_prorata[s] if meta_prorata[s] else 0) for s in real}

        # Rent (do PBI, já normalizado — se período = 9M, pega acquired_ytd; se Q3, acquired_q3)
        if periodo == "Q3-2026":
            rent_real = int(r_rent.get("acquired_q3_brl",0))
            rent_meta = int(r_rent.get("target_q3_brl",0))
        else:
            rent_real = int(r_rent.get("acquired_ytd_brl",0))
            rent_meta = int(int(r_rent.get("target_anual_brl",0)) * fator)
        rent_pct = (100 * rent_real / rent_meta) if rent_meta else 0

        # ─── Nota meta 1 (Pipeline Generation = S1+S3) ───
        # pondera S1 e S3 igualmente
        pct_pipeline = (pct["s1"] + pct["s3"]) / 2
        nota_pipeline = nota_quant(pct_pipeline)

        # ─── Nota meta 2 (Business Results = S99 + Rent) ───
        # S99 e Rent com peso igual
        pct_business = (pct["s99"] + rent_pct) / 2 if rent_meta else pct["s99"]
        nota_business = nota_quant(pct_business)

        diretores.append({
            "nome": nome, "slug": slug(nome), "regime": regime,
            "excluir_quant": False,
            "meta": meta_prorata, "real": real, "pct": pct,
            "rent_meta": rent_meta, "rent_real": rent_real, "rent_pct": rent_pct,
            "pct_pipeline": pct_pipeline, "nota_pipeline": nota_pipeline,
            "pct_business": pct_business, "nota_business": nota_business,
        })
    return diretores

def avaliar_diretor(d, autoaval, periodo):
    """Monta avaliação completa pros 7 metas"""
    av = {}

    # Meta 1 — Pipeline Generation (quantitativo)
    if d["excluir_quant"]:
        av[1] = {"nota":None, "comentario":"Ciclo não aplicável (entrada em jul/2026)", "evidencia":""}
    else:
        extras = f"S1 {d['real']['s1']}/{d['meta']['s1']} ({d['pct']['s1']:.0f}%) · S3 {d['real']['s3']}/{d['meta']['s3']} ({d['pct']['s3']:.0f}%). "
        av[1] = {
            "nota": d["nota_pipeline"],
            "comentario": gerar_comentario_quant(d["nota_pipeline"], "Pipeline Generation",
                f"{d['real']['s1']}+{d['real']['s3']}", f"{d['meta']['s1']}+{d['meta']['s3']}",
                d["pct_pipeline"], extras),
            "evidencia": f"Pipeline Generation = média(%S1, %S3) = {d['pct_pipeline']:.0f}%"
        }

    # Meta 2 — Business Results (quantitativo)
    if d["excluir_quant"]:
        av[2] = {"nota":None, "comentario":"Ciclo não aplicável", "evidencia":""}
    else:
        extras = f"S99 {d['real']['s99']}/{d['meta']['s99']} ({d['pct']['s99']:.0f}%) · Rent R$ {d['rent_real']//1000}k/R$ {d['rent_meta']//1000}k ({d['rent_pct']:.0f}%). "
        av[2] = {
            "nota": d["nota_business"],
            "comentario": gerar_comentario_quant(d["nota_business"], "Business Results",
                "", "", d["pct_business"], extras),
            "evidencia": f"Business Results = média(%S99, %Rent) = {d['pct_business']:.0f}%"
        }

    # Metas 3-7 (qualitativas, dependem de autoavaliação)
    for m in [3,4,5,6,7]:
        aa = autoaval.get(m, {})
        nota, just = nota_qualitativa(aa.get("nota_num"), aa.get("comentario",""), nome_meta=f"Meta {m}")
        av[m] = {
            "nota": nota,
            "comentario": f"{aa.get('comentario','(autoaval não preenchida)')} · Avaliação: {ESCALA_UKG[nota]}.",
            "evidencia": just
        }

    # Nota final ponderada (normaliza pra 100%)
    if d["excluir_quant"]:
        nota_final = None
    else:
        soma = sum(av[m]["nota"] * PESOS[m] for m in av if av[m]["nota"] is not None)
        nota_final = soma / PESO_TOTAL  # normaliza (divide por 95 em vez de 100 corrige a anomalia)
    return av, nota_final

def render_review_html(d, av, nota_final, periodo, data_ref):
    """HTML rico pra revisar antes de colar no UKG"""
    P = PERIODOS[periodo]
    nome = d["nome"]

    rows_metas = []
    for m in [1,2,3,4,5,6,7]:
        meta_nomes = {1:"Pipeline Generation",2:"Business Results",3:"CRM, DEI & Development",
                      4:"Excellence & Attitude",5:"Company Goal: DEI",6:"Company Goal: Training & Development",7:"CRM Usage"}
        n = av[m]["nota"]
        cor = COR_NOTA.get(n, CINZA)
        nota_txt = f'<span style="background:{cor};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:bold;">{n} · {ESCALA_UKG[n]}</span>' if n else '<span style="color:#999;">n/a</span>'
        rows_metas.append(f"""
<tr>
  <td style="padding:10px;border-bottom:1px solid {LINE};vertical-align:top;">
    <b>Meta {m}</b> · {esc(meta_nomes[m])}<br>
    <span style="font-size:11px;color:{CINZA};">peso {PESOS[m]}% · {av[m]["evidencia"]}</span>
  </td>
  <td style="padding:10px;border-bottom:1px solid {LINE};vertical-align:top;">{nota_txt}</td>
  <td style="padding:10px;border-bottom:1px solid {LINE};vertical-align:top;font-size:12.5px;">{esc(av[m]["comentario"])}</td>
</tr>""")

    nota_final_html = ""
    if nota_final is not None:
        cor_f = COR_NOTA.get(round(nota_final), CINZA)
        rotulo_f = ESCALA_UKG.get(round(nota_final), "—")
        nota_final_html = f'<span style="background:{cor_f};color:#fff;padding:6px 20px;border-radius:20px;font-size:16px;font-weight:bold;">{nota_final:.2f} · {rotulo_f}</span>'
    else:
        nota_final_html = '<span style="color:#999;">Não aplicável (ciclo pro-rata insuficiente)</span>'

    # bloco quantitativo
    quant_html = ""
    if not d["excluir_quant"]:
        quant_html = f"""
<h2 style="margin:24px 28px 8px;color:{NAVY};font-size:14px;text-transform:uppercase;border-bottom:2px solid {AZUL};padding-bottom:4px;">Evidência quantitativa ({P["label"]})</h2>
<table style="width:calc(100% - 56px);margin:0 28px;border-collapse:collapse;font-size:12px;">
<tr style="background:{NAVY};color:#fff;">
  <th style="padding:6px 10px;text-align:left;">KPI</th>
  <th style="padding:6px;text-align:right;">Meta pro-rata</th>
  <th style="padding:6px;text-align:right;">Realizado</th>
  <th style="padding:6px;text-align:right;">% atingido</th>
</tr>
<tr><td style="padding:6px 10px;">Stage 1</td><td style="padding:6px;text-align:right;">{d["meta"]["s1"]}</td><td style="padding:6px;text-align:right;">{d["real"]["s1"]}</td><td style="padding:6px;text-align:right;font-weight:bold;color:{COR_NOTA[nota_quant(d['pct']['s1'])]};">{d['pct']['s1']:.0f}%</td></tr>
<tr style="background:{BG2};"><td style="padding:6px 10px;">Stage 3</td><td style="padding:6px;text-align:right;">{d["meta"]["s3"]}</td><td style="padding:6px;text-align:right;">{d["real"]["s3"]}</td><td style="padding:6px;text-align:right;font-weight:bold;color:{COR_NOTA[nota_quant(d['pct']['s3'])]};">{d['pct']['s3']:.0f}%</td></tr>
<tr><td style="padding:6px 10px;">Stage 8 (submissions)</td><td style="padding:6px;text-align:right;">{d["meta"]["s8"]}</td><td style="padding:6px;text-align:right;">{d["real"]["s8"]}</td><td style="padding:6px;text-align:right;font-weight:bold;color:{COR_NOTA[nota_quant(d['pct']['s8'])]};">{d['pct']['s8']:.0f}%</td></tr>
<tr style="background:{BG2};"><td style="padding:6px 10px;">Stage 99 (closed)</td><td style="padding:6px;text-align:right;">{d["meta"]["s99"]}</td><td style="padding:6px;text-align:right;">{d["real"]["s99"]}</td><td style="padding:6px;text-align:right;font-weight:bold;color:{COR_NOTA[nota_quant(d['pct']['s99'])]};">{d['pct']['s99']:.0f}%</td></tr>
<tr><td style="padding:6px 10px;">Rent Acquired (R$)</td><td style="padding:6px;text-align:right;">R$ {d['rent_meta']//1000}k</td><td style="padding:6px;text-align:right;">R$ {d['rent_real']//1000}k</td><td style="padding:6px;text-align:right;font-weight:bold;color:{COR_NOTA[nota_quant(d['rent_pct'])]};">{d['rent_pct']:.0f}%</td></tr>
</table>"""

    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Review {esc(nome)}</title>
<style>
body{{margin:0;padding:0;background:#f4f6fa;font-family:Arial,sans-serif;color:{NAVY};font-size:13px;line-height:1.5;}}
.page{{max-width:860px;margin:24px auto;background:#fff;border:1px solid {LINE};box-shadow:0 2px 12px rgba(0,0,0,0.05);}}
.head{{background:{NAVY};color:#fff;padding:16px 28px;}}
.head .brand{{font-size:11px;opacity:.85;font-weight:bold;}}
.head h1{{margin:4px 0 2px;font-size:22px;font-weight:bold;}}
.head .sub{{font-size:12px;opacity:.9;}}
.final{{text-align:center;padding:16px;background:{BG2};margin:14px 28px;border-radius:4px;}}
.final .label{{font-size:11px;color:{CINZA};text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}}
h2{{color:{NAVY};}}
</style></head><body>
<div class="page">
<div class="head">
  <div class="brand">APW · PERFORMANCE REVIEW · {P["label"].upper()}</div>
  <h1>{esc(nome)}</h1>
  <div class="sub">{esc(d["regime"])} · gerado em {esc(data_ref)}</div>
</div>

<div class="final">
  <div class="label">Nota final ponderada (normalizada {PESO_TOTAL}%→100%)</div>
  {nota_final_html}
</div>

{quant_html}

<h2 style="margin:24px 28px 8px;color:{NAVY};font-size:14px;text-transform:uppercase;border-bottom:2px solid {AZUL};padding-bottom:4px;">Avaliação por meta</h2>
<table style="width:calc(100% - 56px);margin:0 28px;border-collapse:collapse;font-size:12.5px;">
<tr style="background:{NAVY};color:#fff;">
  <th style="padding:8px;text-align:left;">Meta</th>
  <th style="padding:8px;text-align:left;">Nota do Gestor</th>
  <th style="padding:8px;text-align:left;">Comentário</th>
</tr>
{"".join(rows_metas)}
</table>

<div style="margin:22px 28px;padding:14px;background:{BG2};border-left:3px solid {AMBAR};font-size:11.5px;color:{CINZA};">
<b>⚠ Pesos UKG somam 95%</b> (não 100%). Build normalizou dividindo soma por {PESO_TOTAL}. Confirmar com RH se falta categoria.
</div>

<div style="margin:20px 28px;padding-top:12px;border-top:1px solid {LINE};font-size:11px;color:{SAGE};">
Metodologia: Metas 1-2 quantitativas via CRM Dynamics 365 (harvest pace-score + PBI oficial de Rent Acquired).
Metas 3-7 qualitativas via autoavaliação + sinais secundários do CRM.
Régua quantitativa: ≥110% = 4 Exceptional · 90-109% = 3 Exceeds · 70-89% = 2 Meets · <70% = 1 Needs Improvement.
<br>Lucas Minozzo · Director of Acquisitions · APW Brasil
</div>
</div></body></html>"""
    return html

def render_texto_ukg(d, av, nota_final, periodo):
    """Texto pronto pra colar no UKG, meta por meta"""
    P = PERIODOS[periodo]
    meta_nomes = {1:"Pipeline Generation",2:"Business Results",3:"CRM, DEI & Development",
                  4:"Excellence & Attitude",5:"Company Goal: DEI",6:"Company Goal: Training & Development",7:"CRM Usage"}
    out = [f"# Review {d['nome']} — {P['label']}\n"]
    if nota_final is not None:
        out.append(f"**Nota final ponderada: {nota_final:.2f} · {ESCALA_UKG[round(nota_final)]}**\n")
    for m in [1,2,3,4,5,6,7]:
        n = av[m]["nota"]
        rotulo = ESCALA_UKG.get(n, "n/a") if n else "n/a"
        out.append(f"## Meta {m} · {meta_nomes[m]} (peso {PESOS[m]}%)")
        out.append(f"**Nota do Gestor: {rotulo}**")
        out.append(f"{av[m]['comentario']}")
        out.append(f"<!-- evidência: {av[m]['evidencia']} -->\n")
    return "\n".join(out)

def render_consolidado(diretores, resultados, periodo, data_ref):
    """Dashboard do time"""
    P = PERIODOS[periodo]
    rows = []
    for d, (av, nota_final) in zip(diretores, resultados):
        if nota_final is None:
            nota_cell = '<span style="color:#999;">n/a</span>'
            cor = CINZA
        else:
            cor = COR_NOTA.get(round(nota_final), CINZA)
            nota_cell = f'<span style="background:{cor};color:#fff;padding:3px 10px;border-radius:10px;font-weight:bold;">{nota_final:.2f}</span>'
        notas_cells = ""
        for m in [1,2,3,4,5,6,7]:
            n = av[m]["nota"]
            if n:
                c = COR_NOTA[n]
                notas_cells += f'<td style="padding:5px;text-align:center;background:{c};color:#fff;font-weight:bold;">{n}</td>'
            else:
                notas_cells += f'<td style="padding:5px;text-align:center;color:#999;">—</td>'
        rows.append(f'<tr><td style="padding:8px;font-weight:bold;">{esc(d["nome"])}</td><td style="padding:8px;font-size:11px;color:{CINZA};">{esc(d["regime"])}</td>{notas_cells}<td style="padding:8px;text-align:center;">{nota_cell}</td></tr>')

    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Review Consolidado</title></head><body style="font-family:Arial,sans-serif;color:{NAVY};background:#f4f6fa;margin:0;">
<div style="max-width:1100px;margin:24px auto;background:#fff;padding:24px;border:1px solid {LINE};">
<div style="background:{NAVY};color:#fff;padding:14px 20px;margin:-24px -24px 20px;">
  <div style="font-size:11px;opacity:.85;font-weight:bold;">APW · CONSOLIDADO PERFORMANCE REVIEW</div>
  <h1 style="margin:4px 0;font-size:22px;">Time de Aquisições · {P["label"]}</h1>
  <div style="font-size:12px;opacity:.9;">Fotografia em {esc(data_ref)} · {len(diretores)} diretores</div>
</div>
<table style="width:100%;border-collapse:collapse;font-size:12px;">
<tr style="background:{NAVY};color:#fff;">
  <th style="padding:8px;text-align:left;">Diretor</th>
  <th style="padding:8px;text-align:left;">Regime</th>
  <th style="padding:5px;" title="Pipeline Generation 30%">M1</th>
  <th style="padding:5px;" title="Business Results 20%">M2</th>
  <th style="padding:5px;" title="CRM/DEI/Dev 15%">M3</th>
  <th style="padding:5px;" title="Excellence 15%">M4</th>
  <th style="padding:5px;" title="DEI 5%">M5</th>
  <th style="padding:5px;" title="Training 5%">M6</th>
  <th style="padding:5px;" title="CRM Usage 5%">M7</th>
  <th style="padding:8px;">Final</th>
</tr>
{"".join(rows)}
</table>
<div style="margin-top:20px;padding:12px;background:{BG2};border-left:3px solid {AMBAR};font-size:11.5px;color:{CINZA};">
<b>Legenda:</b> M1 Pipeline Generation (30%) · M2 Business Results (20%) · M3 CRM/DEI/Dev (15%) · M4 Excellence (15%) · M5 DEI (5%) · M6 Training (5%) · M7 CRM Usage (5%). Soma 95% — build normaliza.
<br><b>Escala:</b> 4=Exceptional · 3=Exceeds · 2=Meets · 1=Needs Improvement.
<br><b>Marcia</b>: ciclo não aplica (entrou 28/07/2026).
</div>
</div></body></html>"""
    return html

def main():
    harvest_path = arg("harvest")
    rent_csv = arg("rent-pbi", "data/rent_pbi_oficial_2026-10-14.csv")
    inputs_dir = arg("inputs", "inputs/")
    periodo = arg("periodo", "9M-2026")
    out_dir = Path(arg("out", "out/"))
    data_ref = arg("data-ref", date.today().isoformat())

    if not harvest_path:
        print("uso: build_review.py --harvest=X.json --rent-pbi=X.csv --inputs=inputs/ --periodo=9M-2026 --out=out/")
        sys.exit(1)

    harvest = json.load(open(harvest_path))
    diretores = monta_metricas(harvest, rent_csv, periodo)

    out_dir.mkdir(parents=True, exist_ok=True)

    resultados = []
    for d in diretores:
        aa_path = Path(inputs_dir) / d["slug"] / "autoavaliacao.md"
        aa = parse_autoaval(aa_path)
        av, nota_final = avaliar_diretor(d, aa, periodo)
        resultados.append((av, nota_final))

        # pasta do diretor
        dd = out_dir / d["slug"]
        dd.mkdir(exist_ok=True)
        (dd / f"review-{d['slug']}.html").write_text(render_review_html(d, av, nota_final, periodo, data_ref))
        (dd / f"texto-pronto-ukg.md").write_text(render_texto_ukg(d, av, nota_final, periodo))

        # CSV por meta
        with open(dd / "nota-por-meta.csv","w",newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["meta","peso","nota_gestor","rotulo","comentario","evidencia"])
            for m in [1,2,3,4,5,6,7]:
                n = av[m]["nota"]
                w.writerow([m, PESOS[m], n or "", ESCALA_UKG.get(n,"") if n else "n/a",
                            av[m]["comentario"], av[m]["evidencia"]])

    # consolidado
    (out_dir / "consolidado-time.html").write_text(render_consolidado(diretores, resultados, periodo, data_ref))

    # CSV mestre
    with open(out_dir / "consolidado-time.csv","w",newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["diretor","regime","M1_Pipeline","M2_Business","M3_CRM_DEI","M4_Excellence","M5_DEI","M6_Training","M7_CRM_Usage","nota_final"])
        for d, (av, nf) in zip(diretores, resultados):
            w.writerow([d["nome"], d["regime"],
                        av[1]["nota"] or "", av[2]["nota"] or "",
                        av[3]["nota"] or "", av[4]["nota"] or "",
                        av[5]["nota"] or "", av[6]["nota"] or "", av[7]["nota"] or "",
                        f"{nf:.2f}" if nf else "n/a"])

    # metodologia
    (out_dir / "metodologia.md").write_text(f"""# Metodologia da Avaliação

**Período:** {PERIODOS[periodo]["label"]} · pro-rata **{PERIODOS[periodo]["fator"]*100:.0f}%** da meta anual

**Régua quantitativa** (metas 1 e 2):
- ≥ 110% = 4 Exceptional
- 90-109% = 3 Exceeds
- 70-89% = 2 Meets
- < 70% = 1 Needs Improvement

**Metas:**
- Sr Experientes (Fabio, Felipe, José Daniel): S1 100 / S3 60 / S8 12 / S99 10 /ano
- Novos+Plenos: S1 140 / S3 70 / S8 10 / S99 8 /ano
- Rent Acquired: individual por diretor (ver data/rent_pbi_oficial.csv)
- Marcia: pro-rata × 5/12 (não aplicável a este ciclo)

**Pesos UKG:** 30+20+15+15+5+5+5 = **95%** (anomalia). Build normaliza pra 100% (divide por 95). Confirmar RH se falta categoria.

**Rent Acquired:** fonte oficial = Power BI (print 14/10/2026). Target anual é customizado por diretor, não padronizado por regime.
""")

    print(f"✓ Review gerado em {out_dir}")
    print(f"  consolidado-time.html + csv")
    print(f"  {len(diretores)} pastas individuais com review HTML + CSV + texto UKG")
    print(f"\nClassificação final:")
    for d, (_, nf) in sorted(zip(diretores, resultados), key=lambda x: -(x[1][1] or 0)):
        nf_s = f"{nf:.2f}" if nf else " n/a"
        print(f"  {nf_s}  {d['nome']:<22s}  ({d['regime']})")

if __name__ == "__main__":
    main()
