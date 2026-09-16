#!/usr/bin/env python3
"""
apw-erb-towerco-triage — motor de enriquecimento

Transforma a lista RAW da Anatel (planilha "ERBs Mar26": Número Estação,
Operadora, Sigla/UF, MUN, Bairro, Logradouro, Latitude, Longitude, IBGE,
ClassInfraFis, Tecs, Faixa) em SITES FÍSICOS qualificados, e (opcional) cruza
com leads do CRM APW para enriquecer leads sem informação.

VERDADES QUE GOVERNAM O MOTOR
-----------------------------
1. A Anatel licencia por OPERADORA, nunca por torreira. A coluna de torreira
   NÃO existe nos dados raw e não é derivável deles. O motor marca torreira como
   "a confirmar" — fim. Não inventa.
2. O sinal útil da Anatel raw é ClassInfraFis (Greenfield × Rooftop), que mapeia
   no produto APW:
      Rooftop   -> Trilha A (Cessão de Direitos Creditórios / condomínio)
      Greenfield-> Trilha B (Direito Real de Superfície / terreno PF-PJ)
3. Co-location: várias operadoras na mesma estrutura = 1 site = 1 torre.
   O nº de operadoras é indício de tenancy (quanto mais, mais "core" o site).

ENTRADAS
--------
--erb     CSV/planilha Anatel já filtrada por região (export da "ERBs Mar26").
--leads   (opcional) JSON dos leads APW (saída do parseLeads do leadsearch2).
          Campos: lnum, owner, stage, status, address, lat, lng. Se ausente, o
          motor só qualifica os sites Anatel (sem cruzamento).
--radius-colocation  m para agrupar co-location. Default 30.
--radius-match       m para casar site Anatel x lead APW. Default 150.
--region-label       rótulo do recorte (ex.: "São Bernardo do Campo / SP").
--out-prefix         prefixo de saída (.csv e .html).

SAÍDA
-----
Uma linha por SITE FÍSICO: operadoras (tenancy), tipo de infra, TRILHA APW
sugerida, tecnologias, faixa, município/bairro/logradouro, coordenada, link
Maps, torreira="a confirmar", e — se houver leads — status do cruzamento
(já tem lead Lxxxx a Xm  /  SEM lead = prospecção nova).
"""
import argparse, csv, html, json, math, os, unicodedata
from collections import defaultdict


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")


def pick(row, *names):
    low = {strip_accents(k).strip().lower(): v for k, v in row.items()}
    for n in names:
        k = strip_accents(n).strip().lower()
        if k in low and str(low[k]).strip() != "":
            return str(low[k]).strip()
    return None


def haversine(a1, o1, a2, o2):
    R = 6371000.0
    p1, p2 = math.radians(a1), math.radians(a2)
    dla = math.radians(a2 - a1); dlo = math.radians(o2 - o1)
    h = math.sin(dla/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(h))


def norm_op(raw):
    s = strip_accents(raw or "").lower()
    if "telefonica" in s or "vivo" in s: return "Vivo"
    if "claro" in s or "embratel" in s or "america movel" in s: return "Claro"
    if s.strip() == "tim" or "tim " in s or " tim" in s: return "TIM"
    if s.strip() == "oi" or "oi " in s or "telemar" in s: return "Oi"
    if "algar" in s: return "Algar"
    if "brisanet" in s: return "Brisanet"
    return (raw or "?").strip()


def trilha_from_infra(classes):
    """Deriva a trilha APW provável do ClassInfraFis do site (pode ter +1 classe
    se o cluster misturar). Honesto: é sinal de produto, não certeza."""
    cl = {strip_accents(c).lower() for c in classes if c}
    has_roof = any("rooftop" in c or "topo" in c or "predio" in c for c in cl)
    has_green = any("greenfield" in c or "solo" in c for c in cl)
    if has_roof and not has_green:
        return "Trilha A — CDC / condomínio (rooftop)"
    if has_green and not has_roof:
        return "Trilha B — DRS / terreno (greenfield)"
    if has_roof and has_green:
        return "Misto (rooftop + greenfield no cluster) — checar"
    return "Indefinido (ClassInfraFis vazio)"


CANON_COLS = ["Numero Estacao", "Operadora", "Sigla", "MUN", "Bairro",
              "Logradouro", "Latitude", "Longitude", "IBGE", "ClassInfraFis",
              "Tecs", "Faixa"]


def load_erbs(path, uf=None, mun=None, bbox=None):
    """Lê CSV Anatel com OU sem cabeçalho, plano ou .gz.
    A base embutida (assets/anatel_smp_base.csv.gz) vem SEM cabeçalho, no
    layout CANON_COLS. uf/mun/bbox recortam a base nacional antes do motor."""
    import gzip as _gz
    by = {}
    opener = _gz.open if str(path).endswith(".gz") else open
    with opener(path, mode="rt", newline="", encoding="utf-8-sig",
                errors="replace") as f:
        sample = f.read(4096); f.seek(0)
        delim = ";" if sample.count(";") >= sample.count(",") else ","
        first_cell = sample.split("\n", 1)[0].split(delim, 1)[0].strip()
        headerless = first_cell.isdigit()
        reader = csv.DictReader(f, delimiter=delim,
                                fieldnames=CANON_COLS if headerless else None,
                                restkey="_extra")
        for row in reader:
            # ';' extra no logradouro empurra colunas -> reancora pelo fim
            if row.get("_extra"):
                tail = [row["Latitude"], row["Longitude"], row["IBGE"],
                        row["ClassInfraFis"], row["Tecs"], row["Faixa"]] + row["_extra"]
                row["Logradouro"] = delim.join(
                    [row["Logradouro"]] + tail[:len(tail)-6])
                (row["Latitude"], row["Longitude"], row["IBGE"],
                 row["ClassInfraFis"], row["Tecs"], row["Faixa"]) = tail[-6:]
            if uf and strip_accents(pick(row, "Sigla", "UF") or "").upper() != uf.upper():
                continue
            if mun and strip_accents(mun).lower() not in strip_accents(pick(row, "MUN", "Municipio") or "").lower():
                continue
            lat = pick(row, "Latitude", "Lat")
            lng = pick(row, "Longitude", "Long", "Lon", "Lng")
            if not lat or not lng:
                continue
            try:
                lat = float(lat.replace(",", ".")); lng = float(lng.replace(",", "."))
            except ValueError:
                continue
            if not (-34 <= lat <= 6 and -75 <= lng <= -32):
                continue
            if bbox and not (bbox[0] <= lat <= bbox[1] and bbox[2] <= lng <= bbox[3]):
                continue
            num = pick(row, "Número Estação", "Numero Estacao", "NumEstacao", "Estacao") \
                  or f"{lat:.5f},{lng:.5f}"
            if num not in by:
                by[num] = {
                    "num": num, "lat": lat, "lng": lng,
                    "ops": set(), "ufs": set(), "muns": set(), "bairros": set(),
                    "logr": set(), "ibge": set(), "infra": set(), "tecs": set(),
                    "faixas": set(),
                }
            r = by[num]
            r["ops"].add(norm_op(pick(row, "Operadora", "NomeEntidade")))
            for key, col in [("ufs","Sigla"),("muns","MUN"),("bairros","Bairro"),
                             ("logr","Logradouro"),("ibge","IBGE"),
                             ("infra","ClassInfraFis"),("tecs","Tecs"),("faixas","Faixa")]:
                v = pick(row, col)
                if v and strip_accents(v).lower() not in ("vazio", "(vazio)", "-"):
                    r[key].add(v)
    return list(by.values())


def cluster(estacoes, radius):
    n = len(estacoes); parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(n):
        for j in range(i+1, n):
            if haversine(estacoes[i]["lat"], estacoes[i]["lng"],
                         estacoes[j]["lat"], estacoes[j]["lng"]) <= radius:
                parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(estacoes[i])
    sites = []
    for ms in groups.values():
        lat = sum(m["lat"] for m in ms)/len(ms)
        lng = sum(m["lng"] for m in ms)/len(ms)
        agg = {k: set() for k in ("ops","ufs","muns","bairros","logr","ibge","infra","tecs","faixas")}
        for m in ms:
            for k in agg:
                agg[k] |= m[k]
        ops = sorted(o for o in agg["ops"] if o and o != "?")
        sites.append({
            "lat": lat, "lng": lng, "n_estacoes": len(ms),
            "ops": ops, "tenancy": len(ops),
            "uf": " / ".join(sorted(agg["ufs"])),
            "mun": " / ".join(sorted(agg["muns"])),
            "bairro": " / ".join(sorted(agg["bairros"])),
            "logr": " | ".join(sorted(agg["logr"]))[:120],
            "ibge": " / ".join(sorted(agg["ibge"])),
            "infra": " / ".join(sorted(agg["infra"])) or "(vazio)",
            "trilha": trilha_from_infra(agg["infra"]),
            "tecs": " ".join(sorted({t for v in agg["tecs"] for t in v.split()})),
            "faixa": " ".join(sorted({x for v in agg["faixas"] for x in v.split()})),
            "maps": f"https://www.google.com/maps?q={lat:.6f},{lng:.6f}",
        })
    return sites


def load_leads(path):
    with open(path, encoding="utf-8") as f:
        leads = json.load(f)
    out = []
    for ld in leads:
        try:
            ld["lat"] = float(ld["lat"]); ld["lng"] = float(ld["lng"])
        except (KeyError, TypeError, ValueError):
            continue
        out.append(ld)
    return out


def crosscheck(sites, leads, radius_match):
    for s in sites:
        nearest, nd = None, float("inf")
        for ld in leads:
            d = haversine(s["lat"], s["lng"], ld["lat"], ld["lng"])
            if d < nd:
                nd, nearest = d, ld
        if nearest and nd <= radius_match:
            s["crm"] = f"JÁ TEM LEAD {nearest.get('lnum','?')} ({round(nd)} m · {nearest.get('stage') or nearest.get('status') or '—'})"
            s["crm_flag"] = "tem_lead"
        elif nearest:
            s["crm"] = f"sem lead no raio (mais próximo {nearest.get('lnum','?')} a {round(nd)} m) — PROSPECÇÃO"
            s["crm_flag"] = "prospeccao"
        else:
            s["crm"] = "sem leads carregados na região — PROSPECÇÃO"
            s["crm_flag"] = "prospeccao"
    return sites


def write_csv(sites, path, has_leads):
    cols = ["mun","uf","bairro","tenancy","ops","infra","trilha","tecs","faixa",
            "torreira","logr","lat","lng","maps"]
    if has_leads:
        cols.insert(3, "crm")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for s in sites:
            row = {
                "mun": s["mun"], "uf": s["uf"], "bairro": s["bairro"],
                "tenancy": f'{s["tenancy"]} ({", ".join(s["ops"])})',
                "ops": ", ".join(s["ops"]), "infra": s["infra"],
                "trilha": s["trilha"], "tecs": s["tecs"], "faixa": s["faixa"],
                "torreira": "a confirmar (não consta na Anatel)",
                "logr": s["logr"], "lat": f'{s["lat"]:.6f}', "lng": f'{s["lng"]:.6f}',
                "maps": s["maps"],
            }
            if has_leads:
                row["crm"] = s.get("crm", "")
            w.writerow(row)


TR_COLOR = {"A": "#b8860b", "B": "#1e7d4f"}
def trilha_color(t):
    if t.startswith("Trilha A"): return "#b8860b"
    if t.startswith("Trilha B"): return "#1e7d4f"
    return "#7a7a7a"


def write_html(sites, path, label, has_leads):
    n = len(sites)
    n_a = sum(1 for s in sites if s["trilha"].startswith("Trilha A"))
    n_b = sum(1 for s in sites if s["trilha"].startswith("Trilha B"))
    n_multi = sum(1 for s in sites if s["tenancy"] >= 2)
    crm_line = ""
    if has_leads:
        n_lead = sum(1 for s in sites if s.get("crm_flag") == "tem_lead")
        n_pros = n - n_lead
        crm_line = f' · <span style="color:#4e89bd;font-weight:bold">{n_lead} já com lead</span> · <span style="color:#a83232;font-weight:bold">{n_pros} prospecção</span>'
    rows = []
    for i, s in enumerate(sites, 1):
        tc = trilha_color(s["trilha"])
        crm_cell = ""
        if has_leads:
            col = "#4e89bd" if s.get("crm_flag") == "tem_lead" else "#a83232"
            crm_cell = f'<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;font-size:11px;color:{col}">{html.escape(s.get("crm",""))}</td>'
        rows.append(f"""<tr>
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;color:#7a8595;font-size:12px">{i:02d}</td>
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2"><b style="color:#1f2d3d">{html.escape(s['mun'])}</b> <span style="color:#7a8595;font-size:11px">{html.escape(s['uf'])}</span><br><span style="color:#7a8595;font-size:11px">{html.escape(s['bairro'])}</span></td>
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;border-left:4px solid {tc}"><b style="color:{tc};font-size:12px">{html.escape(s['infra'])}</b><br><span style="font-size:11px;color:#4a5563">{html.escape(s['trilha'])}</span></td>
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;font-size:13px;text-align:center"><b>{s['tenancy']}</b><br><span style="color:#7a8595;font-size:11px">{html.escape(', '.join(s['ops']))}</span></td>
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;font-size:11px;color:#4a5563">{html.escape(s['tecs'])}<br><span style="color:#7a8595">{html.escape(s['faixa'])}</span></td>
{crm_cell}
<td style="padding:8px 10px;border-bottom:1px solid #e8edf2;font-family:Consolas,monospace;font-size:11px">{s['lat']:.5f},{s['lng']:.5f}<br><a href="{s['maps']}" style="color:#4e89bd;font-weight:bold;text-decoration:none">abrir ›</a></td>
</tr>""")
    crm_head = '<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">CRM APW</th>' if has_leads else ""
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Enriquecimento ERB — {html.escape(label)}</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;background:#f4f6f9;margin:0;padding:24px">
<div style="max-width:1040px;margin:0 auto;background:#fff;border:1px solid #e0e6ec">
<div style="background:#1f2d3d;padding:20px 28px"><span style="color:#fff;font-size:18px;font-weight:bold">Sites Anatel — qualificação por trilha APW</span><span style="color:#9fb0c2;float:right;font-size:12px">APW Brasil · Aquisições · Confidencial</span><br><span style="color:#9fb0c2;font-size:13px">{html.escape(label)}</span></div>
<div style="padding:16px 28px;background:#f4f8fb;border-bottom:1px solid #e0e6ec;font-size:13px;color:#4a5563"><b>{n}</b> sites físicos · <span style="color:#b8860b;font-weight:bold">{n_a} Trilha A (rooftop)</span> · <span style="color:#1e7d4f;font-weight:bold">{n_b} Trilha B (greenfield)</span> · <b>{n_multi}</b> multi-operadora{crm_line}
<div style="margin-top:8px;font-size:11px;color:#7a8595">⚠ Anatel licencia por <b>operadora</b>, não por torreira — a coluna torreira sai sempre como <b>"a confirmar"</b>. O sinal de produto aqui é o tipo de infra (rooftop→A / greenfield→B), 100% derivado da lista raw.</div></div>
<table style="width:100%;border-collapse:collapse"><thead><tr style="background:#eef2f6">
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">#</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">MUNICÍPIO / BAIRRO</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">INFRA → TRILHA APW</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">TENANCY</th>
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">TEC / FAIXA</th>
{crm_head}
<th style="padding:8px 10px;text-align:left;font-size:11px;color:#5a6573">COORD / MAPS</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table>
<div style="padding:14px 28px;background:#1f2d3d;color:#9fb0c2;font-size:11px">APWireless Brasil Invest. Imob. LTDA · gerado por apw-erb-towerco-triage · torreira sempre "a confirmar" (Anatel = operadora)</div>
</div></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def main():
    ap = argparse.ArgumentParser()
    default_base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "assets", "anatel_smp_base.csv.gz")
    ap.add_argument("--erb", default=default_base,
                    help="CSV Anatel; default = base nacional embutida na skill")
    ap.add_argument("--uf", default=None, help="recorte por UF (ex.: SP)")
    ap.add_argument("--mun", default=None, help="recorte por município (substring)")
    ap.add_argument("--bbox", default=None,
                    help="recorte lat_min,lat_max,lng_min,lng_max")
    ap.add_argument("--leads", default=None)
    ap.add_argument("--radius-colocation", type=float, default=30.0)
    ap.add_argument("--radius-match", type=float, default=150.0)
    ap.add_argument("--region-label", default="região não informada")
    ap.add_argument("--out-prefix", default="/mnt/user-data/outputs/erb_enriquecimento")
    a = ap.parse_args()

    if a.erb == default_base and not (a.uf or a.mun or a.bbox):
        ap.error("usando a base nacional embutida: informe --uf, --mun ou --bbox "
                 "(nunca rode o Brasil inteiro no motor)")
    bbox = tuple(float(x) for x in a.bbox.split(",")) if a.bbox else None
    est = load_erbs(a.erb, uf=a.uf, mun=a.mun, bbox=bbox)
    print(f"[erb] {len(est)} estações únicas (dedup por Número Estação)")
    sites = cluster(est, a.radius_colocation)
    print(f"[site] {len(sites)} sites físicos após co-location (<= {a.radius_colocation:.0f} m)")
    has_leads = bool(a.leads and os.path.exists(a.leads))
    if has_leads:
        leads = load_leads(a.leads)
        print(f"[crm] {len(leads)} leads APW carregados")
        crosscheck(sites, leads, a.radius_match)
    # ordenar: multi-operadora primeiro, depois por trilha
    sites.sort(key=lambda s: (-s["tenancy"], s["trilha"]))
    os.makedirs(os.path.dirname(a.out_prefix) or ".", exist_ok=True)
    write_csv(sites, a.out_prefix + ".csv", has_leads)
    write_html(sites, a.out_prefix + ".html", a.region_label, has_leads)
    na = sum(1 for s in sites if s["trilha"].startswith("Trilha A"))
    nb = sum(1 for s in sites if s["trilha"].startswith("Trilha B"))
    print(f"[out] {a.out_prefix}.csv/.html — {na} Trilha A, {nb} Trilha B, "
          f"{sum(1 for s in sites if s['tenancy']>=2)} multi-operadora")


if __name__ == "__main__":
    main()
