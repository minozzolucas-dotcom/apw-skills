#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APW Stage 1 Quality Audit — motor de scoring + render.

Uso:
  python3 build_audit.py score  raw.json audit.json
  python3 build_audit.py render audit.json <outdir> <YYYY-MM-DD>

`score`  : aplica a rubrica (references/qualification-rubric.md), calcula métricas do
           cohort, atribui tier por opp e extrai frases-evidência -> audit.json.
`render` : audit.json -> PNG board-executivo (marca APW) + anexo Markdown de evidências.

O modelo revisa audit.json (tiers borderline) entre score e render.
"""
import sys, json, re, os, html, statistics, subprocess, datetime, shutil

# ----------------------------- léxicos (rubrica) -----------------------------
SUBST_SIGNALS = [
    r"\b(r\$|\d{1,3}(\.\d{3})*(,\d{2})?|\d+\s?(reais|mil|k))\b",
    r"\b(s[íi]ndico|propriet[áa]ri|administrador|condom[íi]nio|operadora|torre|locador|advogad)",
    r"\b(pr[óo]ximo passo|retornar|agendar|enviar|aguard|follow|reuni[ãa]o|visita|proposta|marcar|ligar)",
    r"\b(obje[çc]|recus|negocia[çc]|contraproposta|exig|condi[çc]|quer|pediu|preocupa)",
]
AUTO = [r"^\s*$", r"^opportunity .*(created|updated|reassigned)", r"^lead .*(created|qualified|disqualified)",
        r"^workflow .*(executed|triggered)", r"^the (stage|status) .* was (changed|updated)",
        r"^atividade gerada pelo sistema", r"^reminder:", r"notifica[çc][ãa]o autom[áa]tica"]
DECISOR_POS = [r"s[íi]ndic", r"propriet[áa]ri", r"\bdon[oa] d", r"decisor", r"respons[áa]vel pelo",
               r"procurador", r"\bs[óo]cio\b", r"gestor predial", r"presidente do conselho",
               r"quem decide", r"\b[ée] o dono\b", r"titular da matr[íi]cula", r"herdeir",
               r"inventariante", r"representante legal", r"administrador[a]?\s+\w+"]
DECISOR_NEG = [r"porteir", r"zelador", r"recep[çc]", r"secret[áa]ri", r"atendente",
               r"falei com o pessoal", r"recado na portaria", r"n[ãa]o soube (dizer|informar) quem",
               r"ningu[ée]m sabia informar"]
PITCH_POS = [r"apresentei", r"expliquei o modelo", r"como funciona", r"cess[ãa]o de cr[ée]dito",
             r"cess[ãa]o de direitos credit[óo]rios", r"\bdrs\b", r"direito real de superf[íi]cie",
             r"antecipa[çc][ãa]o de aluguel", r"compra do fluxo", r"mostrei a proposta",
             r"enviei a minuta", r"passei o material", r"\bpitch\b",
             r"achou interessante", r"vai analisar", r"pediu a minuta", r"pediu pra ver o contrato",
             r"levou pra assembleia", r"tem d[úu]vida sobre", r"questionou", r"obje[çc][ãa]o",
             r"contraproposta", r"pediu mais informa[çc]"]
PITCH_NEG = [r"liguei,? n[ãa]o atendeu", r"vou retornar", r"deixei recado", r"sem retorno",
             r"aguardando", r"tentando contato", r"n[úu]mero errado", r"caixa postal"]
RE_PHONE = re.compile(r"(\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4})")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
CONTATO_POS = [r"contato:", r"salvei o contato", r"cadastrei no crm", r"dados do s[íi]ndico",
               r"telefone do propriet[áa]ri"]
# PII a redigir no anexo (mantém papel/nome/telefone como evidência; mascara doc e valor)
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
RE_MONEY = re.compile(r"r\$\s?\d{1,3}(\.\d{3})*(,\d{2})?", re.I)

def anyx(pats, t): return any(re.search(p, t, re.I) for p in pats)
def is_auto(d): return (not d) or (not d.strip()) or anyx(AUTO, d.strip())
def is_subst(d):
    if not d: return False
    L = len(d.strip())
    return L >= 180 or (L >= 140 and sum(bool(re.search(s, d, re.I)) for s in SUBST_SIGNALS) >= 2)

def redact(t):
    t = RE_CPF.sub("[CPF]", t); t = RE_CNPJ.sub("[CNPJ]", t); t = RE_MONEY.sub("[R$]", t)
    return t

def snippet(d, pats, maxlen=160):
    """menor trecho que contém o 1º match de pats."""
    for p in pats:
        m = re.search(p, d, re.I)
        if m:
            i = max(0, m.start() - 50); j = min(len(d), m.end() + 70)
            s = d[i:j].strip().replace("\n", " ")
            return ("…" if i else "") + redact(s)[:maxlen] + ("…" if j < len(d) else "")
    return None

# ----------------------------- scoring -----------------------------
def parse_date(s):
    if not s: return None
    try: return datetime.date.fromisoformat(s[:10])
    except Exception: return None

def score_opp(o, today):
    acts = o.get("acts", [])
    real = [a for a in acts if not (a.get("auto") and is_auto(a.get("desc", "")))]
    subst = [a for a in real if is_subst(a.get("desc", ""))]
    blob = "\n".join(a.get("desc", "") for a in subst) or "\n".join(a.get("desc", "") for a in real)

    decisor_pos = anyx(DECISOR_POS, blob)
    decisor_neg = anyx(DECISOR_NEG, blob)
    p_decisor = decisor_pos                       # positivo prevalece sobre negativo
    p_pitch = anyx(PITCH_POS, blob) and not (anyx(PITCH_NEG, blob) and not anyx(PITCH_POS, blob))
    p_pitch = anyx(PITCH_POS, blob)
    p_contato = bool(RE_PHONE.search(blob) or RE_EMAIL.search(blob) or anyx(CONTATO_POS, blob))
    pillars = {"decisor": bool(p_decisor), "pitch": bool(p_pitch), "contato": bool(p_contato)}
    nfilled = sum(pillars.values())

    # status
    s1 = parse_date(o.get("stage1_date")); s3 = parse_date(o.get("stage3_date"))
    surr = o.get("surrender_reason")
    if s3: status = "evolved"
    elif surr: status = "surrendered"
    else: status = "still_s1"
    days_s1 = (today - s1).days if s1 else None
    fast_surrender = status == "surrendered" and days_s1 is not None and days_s1 <= 14 and \
                     parse_date(o.get("stage1_date")) is not None  # aprox; surrender date nem sempre vem

    # tier
    if nfilled == 3:
        tier, reason = "solida", "3 pilares evidenciados"
    elif nfilled >= 1:
        tier = "rasa"
        falta = [k for k, v in pillars.items() if not v]
        reason = "pilar(es) faltando: " + ", ".join(falta)
        if days_s1 is not None and days_s1 <= 7:
            reason += " · qualificação recente (≤7d), pouco tempo de registro"
    else:
        if days_s1 is not None and days_s1 <= 7:
            tier, reason = "rasa", "0 pilares mas qualificação muito recente (≤7d) — cedo pra julgar, revisar texto"
        elif not subst:
            tier, reason = "suspeita", "0 pilares e nenhuma atividade substantiva (só fina/automática)"
        else:
            tier, reason = "rasa", "0 pilares mas há atividade substantiva — revisar texto"
    # reforços de suspeita
    if tier == "suspeita":
        extra = []
        if status == "still_s1" and days_s1 is not None and days_s1 >= 30:
            extra.append(f"segue em S1 há {days_s1}d sem substantiva")
        if fast_surrender and nfilled <= 1:
            extra.append("surrender ≤14d pós-qualificação rasa")
        if extra: reason += " · " + " · ".join(extra)

    # evidências (até 3, dos pilares cumpridos; senão amostra do registro)
    ev = []
    src = {"decisor": DECISOR_POS, "pitch": PITCH_POS, "contato": CONTATO_POS + [RE_PHONE.pattern, RE_EMAIL.pattern]}
    for a in subst or real:
        d = a.get("desc", "")
        for pil, pats in src.items():
            if pillars[pil]:
                sn = snippet(d, pats)
                if sn and all(sn != e["quote"] for e in ev):
                    ev.append({"date": (a.get("created") or "")[:10], "owner": a.get("owner", ""),
                               "pillar": pil, "quote": sn})
        if len(ev) >= 3: break
    if not ev and (subst or real):
        a = (subst or real)[0]
        ev.append({"date": (a.get("created") or "")[:10], "owner": a.get("owner", ""),
                   "pillar": "—", "quote": redact((a.get("desc", "") or "—").strip().replace("\n", " "))[:160]})

    return {"L": o.get("L", "?"), "owner": o.get("owner", "—"), "is_pool": o.get("is_pool", False),
            "owner_is_director": o.get("owner_is_director", False),
            "status": status, "surrender_reason": surr, "fast_surrender": bool(fast_surrender),
            "property_type": o.get("property_type") or "—",
            "stage1_date": o.get("stage1_date"), "stage3_date": o.get("stage3_date"),
            "days_in_s1": days_s1, "n_acts": len(acts), "n_subst": len(subst),
            "pillars": pillars, "tier": tier, "tier_reason": reason, "evidence": ev}

def do_score(raw_path, out_path):
    raw = json.load(open(raw_path, encoding="utf-8"))
    if raw.get("error"):
        print("ERRO na coleta:", raw["error"]); sys.exit(1)
    today = datetime.date.today()
    opps = [score_opp(o, today) for o in raw.get("opps", [])]

    coh = {"total": len(opps), "evolved_s3": 0, "still_s1": 0, "surrendered": 0, "fast_surrender": 0,
           "surrender_reasons": {}, "property_type": {}, "owner": {"person": 0, "pool": 0, "by_director": {}}}
    for o in opps:
        coh["evolved_s3"] += o["status"] == "evolved"
        coh["still_s1"] += o["status"] == "still_s1"
        coh["surrendered"] += o["status"] == "surrendered"
        coh["fast_surrender"] += o["fast_surrender"]
        if o["status"] == "surrendered":
            k = o["surrender_reason"] or "(motivo em branco)"
            coh["surrender_reasons"][k] = coh["surrender_reasons"].get(k, 0) + 1
        pt = o["property_type"] or "—"
        coh["property_type"][pt] = coh["property_type"].get(pt, 0) + 1
        if o["owner_is_director"]:
            coh["owner"]["person"] += 1
            coh["owner"]["by_director"][o["owner"]] = coh["owner"]["by_director"].get(o["owner"], 0) + 1
        else:
            coh["owner"]["pool"] += 1

    # rollup por diretor
    dirs = {}
    for o in opps:
        if not o["owner_is_director"]: continue
        d = dirs.setdefault(o["owner"], {"name": o["owner"], "n_cohort": 0, "n_solida": 0,
                                         "n_rasa": 0, "n_suspeita": 0, "_subst": []})
        d["n_cohort"] += 1; d["_subst"].append(o["n_subst"])
        d["n_" + {"solida": "solida", "rasa": "rasa", "suspeita": "suspeita"}[o["tier"]]] += 1
    dl = []
    for d in dirs.values():
        n = d["n_cohort"]; pct = d["n_suspeita"] / n if n else 0
        d["pct_suspeita"] = round(pct, 3)
        d["median_subst"] = round(statistics.median(d.pop("_subst") or [0]), 1)
        dl.append(d)
    med = statistics.median([d["pct_suspeita"] for d in dl]) if dl else 0
    for d in dl:
        if d["n_cohort"] < 5:
            d["flag"] = "inconclusivo"
        elif d["pct_suspeita"] >= 0.30 or d["pct_suspeita"] >= med + 0.15:
            d["flag"] = "atencao"
        else:
            d["flag"] = "none"
    dl.sort(key=lambda x: (-x["pct_suspeita"], -x["n_cohort"]))

    audit = {"year": raw.get("year"), "generated": today.isoformat(),
             "_meta": {"columns_discovered": raw.get("_meta", {}).get("columns_discovered"),
                       "host": raw.get("host"), "team_median_pct_suspeita": round(med, 3)},
             "cohort": coh, "directors": dl, "opps": opps}
    json.dump(audit, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"OK score -> {out_path}")
    print(f"  cohort {coh['total']} | S3 {coh['evolved_s3']} | S1 {coh['still_s1']} | "
          f"surr {coh['surrendered']} ({coh['fast_surrender']} rápidos)")
    print(f"  tiers: 🟢 {sum(o['tier']=='solida' for o in opps)} "
          f"🟡 {sum(o['tier']=='rasa' for o in opps)} 🔴 {sum(o['tier']=='suspeita' for o in opps)}")

# ----------------------------- render -----------------------------
BRAND = {"navy": "#012B5E", "azul": "#1C75BB", "sage": "#91A5A4", "verde": "#009877",
         "oliva": "#A7AF00", "cinza": "#5D5D5D", "susp": "#A6342B", "bg": "#f4f7fa", "box": "#eef2f6"}

def bar(label, n, total, color, w=320):
    pct = (n / total * 100) if total else 0
    return (f'<div class="brow"><span class="blab">{html.escape(str(label))}</span>'
            f'<span class="btrack" style="width:{w}px"><span class="bfill" style="width:{pct:.0f}%;background:{color}"></span></span>'
            f'<span class="bval">{n}</span></div>')

def build_html(a):
    c = a["cohort"]; b = BRAND; year = a.get("year", "")
    tot = c["total"] or 1
    ev_pct = c["evolved_s3"] / tot * 100
    # funil
    funnel = f"""
    <div class="funnel">
      <div class="fstep"><div class="fn">{c['total']}</div><div class="fl">Stage 1 movidos em {year}</div></div>
      <div class="farr">→</div>
      <div class="fstep"><div class="fn" style="color:{b['verde']}">{c['evolved_s3']}</div><div class="fl">Evoluíram p/ Stage 3<br><b>{ev_pct:.0f}%</b> · proposta enviada</div></div>
      <div class="farr">→</div>
      <div class="fstep"><div class="fn" style="color:{b['azul']}">{c['still_s1']}</div><div class="fl">Seguem em Stage 1<br>em andamento</div></div>
      <div class="farr">→</div>
      <div class="fstep"><div class="fn" style="color:{b['susp']}">{c['surrendered']}</div><div class="fl">Surrendered<br>{c['fast_surrender']} rápidos (≤14d)</div></div>
    </div>"""
    # property type + owner
    pt = sorted(c["property_type"].items(), key=lambda x: -x[1])[:6]
    pt_bars = "".join(bar(k, v, tot, b["sage"], 220) for k, v in pt)
    own = c["owner"]
    own_bars = bar("Diretor (pessoa)", own["person"], tot, b["azul"], 220) + bar("Pool / sistema", own["pool"], tot, b["sage"], 220)
    topd = sorted(own["by_director"].items(), key=lambda x: -x[1])[:5]
    topd_bars = "".join(bar(k, v, tot, b["navy"], 220) for k, v in topd)
    # surrender reasons
    sr = sorted(c["surrender_reasons"].items(), key=lambda x: -x[1])
    sr_html = "".join(f'<li><b>{v}</b> · {html.escape(str(k))}</li>' for k, v in sr) or "<li>—</li>"
    # scorecard
    rows = ""
    for d in a["directors"]:
        fl = {"atencao": f'<span class="flag fa">atenção</span>',
              "inconclusivo": f'<span class="flag fi">amostra peq.</span>',
              "none": ""}[d["flag"]]
        rowcls = "hl" if d["flag"] == "atencao" else ""
        rows += (f'<tr class="{rowcls}"><td class="dn">{html.escape(d["name"])}</td>'
                 f'<td>{d["n_cohort"]}</td>'
                 f'<td style="color:{b["verde"]}">{d["n_solida"]}</td>'
                 f'<td style="color:{b["oliva"]}">{d["n_rasa"]}</td>'
                 f'<td style="color:{b["susp"]};font-weight:700">{d["n_suspeita"]}</td>'
                 f'<td style="font-weight:700">{d["pct_suspeita"]*100:.0f}%</td>'
                 f'<td>{fl}</td></tr>')
    # headline suspeitas
    susp = [o for o in a["opps"] if o["tier"] == "suspeita" and o["owner_is_director"]]
    susp.sort(key=lambda o: (-(o["days_in_s1"] or 0)))
    n_susp = len(susp)
    sus_html = "".join(
        f'<li><b>{html.escape(o["L"])}</b> · {html.escape(o["owner"])} · '
        f'{html.escape(o["status"].replace("still_s1","segue S1").replace("evolved","S3").replace("surrendered","surr"))}'
        f' — {html.escape(o["tier_reason"])}</li>' for o in susp[:12]) or "<li>Nenhuma suspeita 🔴 no cohort.</li>"
    susp_title = f"SUSPEITAS 🔴 — {n_susp} no cohort" + (f" · top 12 mais antigas em S1" if n_susp > 12 else "")

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,Helvetica,sans-serif;background:#fff;color:{b['navy']};width:1120px}}
.wrap{{width:1120px;padding:0}}
.head{{background:{b['navy']};color:#fff;padding:22px 30px;display:flex;justify-content:space-between;align-items:flex-end}}
.wm{{font-size:22px;font-weight:bold}} .wm .br{{color:{b['sage']}}}
.htitle{{text-align:right}} .htitle .t{{font-size:20px;font-weight:bold}} .htitle .s{{font-size:13px;color:{b['sage']}}}
.body{{padding:24px 30px}}
.sec{{margin-bottom:22px}} .sec h3{{font-size:14px;color:{b['azul']};border-bottom:2px solid {b['azul']};padding-bottom:4px;margin-bottom:12px;letter-spacing:.3px}}
.funnel{{display:flex;align-items:center;justify-content:space-between;background:{b['bg']};border-radius:10px;padding:18px 14px}}
.fstep{{text-align:center;flex:1}} .fn{{font-size:34px;font-weight:bold}} .fl{{font-size:12px;color:{b['cinza']};margin-top:4px;line-height:1.3}}
.farr{{font-size:24px;color:{b['sage']};padding:0 6px}}
.cols{{display:flex;gap:26px}} .col{{flex:1}}
.brow{{display:flex;align-items:center;margin-bottom:7px;font-size:12px}}
.blab{{width:140px;color:{b['cinza']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.btrack{{display:inline-block;height:14px;background:{b['box']};border-radius:7px;overflow:hidden;margin:0 8px}}
.bfill{{display:block;height:14px;border-radius:7px}} .bval{{font-weight:bold;min-width:24px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:{b['navy']};color:#fff;padding:7px 8px;text-align:center;font-size:12px}}
th:first-child,td:first-child{{text-align:left}}
td{{padding:6px 8px;border-bottom:1px solid {b['box']};text-align:center}}
.dn{{font-weight:bold;color:{b['navy']}}}
tr.hl{{background:#FBFBEF}}
.flag{{font-size:11px;padding:2px 7px;border-radius:9px;color:#fff}}
.fa{{background:{b['oliva']}}} .fi{{background:{b['sage']}}}
ul{{list-style:none;font-size:12.5px;line-height:1.7}} ul li{{padding-left:14px;position:relative;color:{b['cinza']}}}
ul li:before{{content:"›";position:absolute;left:0;color:{b['azul']};font-weight:bold}}
ul li b{{color:{b['navy']}}}
.foot{{background:{b['box']};padding:12px 30px;font-size:11px;color:{b['cinza']};display:flex;justify-content:space-between}}
.disc{{font-style:italic}}
</style></head><body><div class="wrap">
<div class="head">
  <div class="wm">APW<span class="br">Brasil</span></div>
  <div class="htitle"><div class="t">Auditoria de Qualificação · Stage 1 {year}</div>
    <div class="s">Gerado em {a.get('generated','')} · cohort de {c['total']} oportunidades · mediana suspeita do time {a['_meta'].get('team_median_pct_suspeita',0)*100:.0f}%</div></div>
</div>
<div class="body">
  <div class="sec"><h3>FUNIL DO COHORT</h3>{funnel}</div>
  <div class="sec"><div class="cols">
    <div class="col"><h3>PROPERTY TYPE</h3>{pt_bars}</div>
    <div class="col"><h3>ONDE ESTÁ A OPP (OWNER)</h3>{own_bars}<div style="height:8px"></div>{topd_bars}</div>
  </div></div>
  <div class="sec"><h3>SCORECARD DE INTEGRIDADE POR DIRETOR</h3>
    <table><tr><th>Diretor</th><th>Cohort S1</th><th>🟢 Sólida</th><th>🟡 Rasa</th><th>🔴 Suspeita</th><th>% Susp.</th><th>Flag</th></tr>{rows}</table>
  </div>
  <div class="sec"><div class="cols">
    <div class="col"><h3>{susp_title}</h3><ul>{sus_html}</ul></div>
    <div class="col"><h3>SURRENDERS POR MOTIVO</h3><ul>{sr_html}</ul></div>
  </div></div>
</div>
<div class="foot"><span>APWireless Brasil Invest. Imob. LTDA</span>
  <span class="disc">Sinais para investigar, não veredito. Cada flag tem evidência no anexo.</span></div>
</div></body></html>"""

def html_to_png(html_path, png_path):
    """tenta playwright -> chrome headless subprocess. Retorna True se gerou PNG."""
    try:
        from playwright.sync_api import sync_playwright
        chrome = None
        for p in ["/opt/google/chrome/chrome", shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]:
            if p and os.path.exists(p): chrome = p; break
        with sync_playwright() as pw:
            kw = {"executable_path": chrome} if chrome else {}
            br = pw.chromium.launch(**kw)
            pg = br.new_page(viewport={"width": 1120, "height": 1000}, device_scale_factor=2)
            pg.goto("file://" + os.path.abspath(html_path))
            pg.wait_for_timeout(300)
            pg.locator(".wrap").screenshot(path=png_path)
            br.close()
        return os.path.exists(png_path)
    except Exception as e:
        print("  [png via playwright falhou]", e)
    for exe in ["/opt/google/chrome/chrome", shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]:
        if exe and os.path.exists(exe):
            try:
                subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu",
                                "--window-size=1120,1400", f"--screenshot={png_path}",
                                "file://" + os.path.abspath(html_path)],
                               check=True, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(png_path): return True
            except Exception as e:
                print("  [png via", exe, "falhou]", e)
    return False

def build_md(a, full=False):
    c = a["cohort"]; tot = c["total"] or 1
    tmap = {"solida": "🟢 Sólida", "rasa": "🟡 Rasa", "suspeita": "🔴 Suspeita"}
    stmap = {"still_s1": "segue S1", "evolved": "→S3", "surrendered": "surrender"}
    L = [f"# Auditoria de Qualificação Stage 1 {a.get('year','')} — anexo de evidências",
         f"\n_Gerado em {a.get('generated','')} · cohort {c['total']} oportunidades · "
         f"mediana suspeita do time {a['_meta'].get('team_median_pct_suspeita',0)*100:.0f}%_",
         "\n> Cada tier 🔴/🟡 é **sinal para investigar**, sustentado pela frase-evidência "
         "(data · dono). Registro fino pode ser trabalho real mal documentado — verifique antes de concluir.\n"]

    # ---- resumo executivo / triagem ----
    n_sol = sum(o["tier"] == "solida" for o in a["opps"])
    n_ras = sum(o["tier"] == "rasa" for o in a["opps"])
    n_sus = sum(o["tier"] == "suspeita" for o in a["opps"])
    L.append("## Resumo executivo")
    L.append(f"\n- **Funil:** {c['total']} S1 → {c['evolved_s3']} evoluíram p/ Stage 3 "
             f"({c['evolved_s3']/tot*100:.0f}%) · {c['still_s1']} seguem em S1 · "
             f"{c['surrendered']} surrendered ({c['fast_surrender']} rápidos ≤14d).")
    L.append(f"- **Tiers:** 🟢 {n_sol} Sólida · 🟡 {n_ras} Rasa · 🔴 {n_sus} Suspeita.")
    flagged = [d for d in a["directors"] if d["flag"] == "atencao"]
    if flagged:
        L.append("- **Diretores em atenção (outliers de suspeita):** " +
                 "; ".join(f"{d['name']} ({d['n_suspeita']}/{d['n_cohort']} = {d['pct_suspeita']*100:.0f}%)" for d in flagged) + ".")
    else:
        L.append("- **Diretores em atenção:** nenhum outlier acima do limiar (com cohort ≥5).")
    # prioridade: still_s1 suspeita, mais antigas primeiro
    prio = [o for o in a["opps"] if o["tier"] == "suspeita" and o["status"] == "still_s1" and o["owner_is_director"]]
    prio.sort(key=lambda o: -(o["days_in_s1"] or 0))
    L.append(f"\n### 🔴 Prioridade de investigação — seguem em S1 sem lastro ({len(prio)})")
    if prio:
        for o in prio[:30]:
            L.append(f"- **{o['L']}** · {o['owner']} · {o['days_in_s1']}d em S1 · {o['property_type']} — {o['tier_reason']}")
        if len(prio) > 30: L.append(f"- … +{len(prio)-30} (lista completa por diretor abaixo).")
    else:
        L.append("- Nenhuma. 🔴 Suspeitas, se houver, são casos já evoluídos/surrendered (ver por diretor).")

    # ---- por diretor ----
    L.append("\n---\n## Detalhe por diretor")
    for d in a["directors"]:
        L.append(f"\n### {d['name']} — cohort {d['n_cohort']} · "
                 f"🟢{d['n_solida']} 🟡{d['n_rasa']} 🔴{d['n_suspeita']} · "
                 f"{d['pct_suspeita']*100:.0f}% suspeita"
                 + (f" · ⚠️ {d['flag']}" if d["flag"] != "none" else ""))
        opps = [o for o in a["opps"] if o["owner"] == d["name"] and o["owner_is_director"]]
        opps.sort(key=lambda o: ({"suspeita": 0, "rasa": 1, "solida": 2}[o["tier"]], -(o["days_in_s1"] or 0)))
        sol_line = []
        for o in opps:
            if o["tier"] == "solida" and not full:
                sol_line.append(o["L"]); continue
            pil = " ".join(("✓" if v else "✗") + k[0].upper() for k, v in o["pillars"].items())
            L.append(f"\n**{o['L']}** · {tmap[o['tier']]} · {stmap[o['status']]} · {o['property_type']} · "
                     f"{o['n_subst']} ativ. subst. · pilares [{pil}]"
                     + (f" · {o['days_in_s1']}d em S1" if o["days_in_s1"] is not None else ""))
            L.append(f"  - _motivo:_ {o['tier_reason']}")
            for e in o["evidence"]:
                L.append(f"  - _{e['date']} · {e['owner']} · {e['pillar']}:_ \"{e['quote']}\"")
        if sol_line:
            L.append(f"\n🟢 **Sólidas ({len(sol_line)})** _(sem detalhe — 3 pilares ok):_ " + ", ".join(sol_line))
    return "\n".join(L)

def do_render(audit_path, outdir, date, full=False):
    a = json.load(open(audit_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    base = f"auditoria-stage1-{a.get('year','')}-{date}"
    html_path = os.path.join(outdir, base + ".html")
    png_path = os.path.join(outdir, base + ".png")
    md_path = os.path.join(outdir, base + "-evidencias.md")
    open(html_path, "w", encoding="utf-8").write(build_html(a))
    open(md_path, "w", encoding="utf-8").write(build_md(a, full=full))
    ok = html_to_png(html_path, png_path)
    print(f"OK render -> {md_path}")
    if ok: print(f"OK render -> {png_path}")
    else:  print(f"[!] PNG não gerado (sem Chrome headless). HTML pronto em {html_path} — abra e exporte, ou rode onde haja Chrome.")
    print(f"    HTML -> {html_path}")

# ----------------------------- cli -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("score", "render"):
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "score":
        do_score(sys.argv[2], sys.argv[3])
    else:
        full = "--full" in sys.argv
        args = [x for x in sys.argv[2:] if x != "--full"]
        do_render(args[0], args[1], args[2] if len(args) > 2 else datetime.date.today().isoformat(), full=full)
