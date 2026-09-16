#!/usr/bin/env python3
"""
anatel_lookup.py — consulta pontual à BASE ANATEL LOCAL embutida na skill.

Base: assets/anatel_smp_base.csv.gz (extração fornecida pelo Lucas em jul/2026,
arquivo original "Mai26.csv" — 111.296 estações SMP únicas, 27 UFs, sem header).

Layout (12 colunas, separador ';', SEM cabeçalho):
  Estação; Operadora; UF; Município; Bairro; Logradouro; Lat; Long; IBGE;
  ClassInfraFis; Tecs; Faixas
Linhas com ';' extra no logradouro são reparadas ancorando pelos 6 campos
finais (lat, lng, ibge, infra, tecs, faixa).

MODOS (combináveis; qualquer filtro reduz o conjunto):
  --near LAT,LNG [--radius M]   sites num raio (default 300 m)
  --estacao NUM                 nº de estação exato
  --mun "NOME" [--uf XX]        município (sem acento, case-insensitive)
  --bairro "NOME"               substring do bairro
  --addr "TRECHO"               substring do logradouro
  --operadora VIVO              filtra operadora
  --uf SP                       filtra UF
  --cluster                     agrupa co-location (30 m) => 1 linha por SITE
  --limit N                     máx. de linhas exibidas (default 30)
  --json                        saída JSON (para outras skills consumirem)

Exemplos:
  python3 anatel_lookup.py --near -23.48298,-46.64489 --radius 200
  python3 anatel_lookup.py --addr "CONSELHEIRO MOREIRA DE BARROS" --uf SP
  python3 anatel_lookup.py --mun "Juiz de Fora" --bairro BANDEIRANTES --cluster
"""
import argparse, csv, gzip, io, json, math, os, sys, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "assets", "anatel_smp_base.csv.gz")
COLS = ["estacao", "operadora", "uf", "mun", "bairro", "logradouro",
        "lat", "lng", "ibge", "infra", "tecs", "faixa"]

TRILHA = {"rooftop": "Trilha A — CDC (condomínio)",
          "greenfield": "Trilha B — DRS (terreno)"}


def norm(s):
    s = unicodedata.normalize("NFD", (s or ""))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip().lower()


def haversine(a1, o1, a2, o2):
    R = 6371000.0
    p1, p2 = math.radians(a1), math.radians(a2)
    dp, dl = math.radians(a2 - a1), math.radians(o2 - o1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))


def parse_row(line):
    p = line.rstrip("\r\n").split(";")
    if len(p) < 12:
        return None
    if len(p) > 12:  # ';' extra dentro do logradouro -> ancorar pelo fim
        p = p[:5] + [";".join(p[5:len(p)-6])] + p[len(p)-6:]
    r = dict(zip(COLS, (x.strip() for x in p)))
    try:
        r["lat"], r["lng"] = float(r["lat"]), float(r["lng"])
    except ValueError:
        return None
    if not (-35 <= r["lat"] <= 6 and -75 <= r["lng"] <= -32):
        return None  # coordenada fora do Brasil / linha corrompida
    return r


def load(path=BASE):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8", errors="replace") as f:
        first = f.readline()
        # tolera base futura COM header
        if not norm(first).startswith(("numero", "estac")) or first.split(";")[0].strip().isdigit():
            r = parse_row(first)
            if r:
                yield r
        for line in f:
            r = parse_row(line)
            if r:
                yield r


def trilha(infra):
    n = norm(infra)
    if "rooftop" in n and "greenfield" not in n:
        return TRILHA["rooftop"]
    if "greenfield" in n and "rooftop" not in n:
        return TRILHA["greenfield"]
    if "rooftop" in n and "greenfield" in n:
        return "Mista (verificar) — GF+RT"
    return "indefinido (ClassInfraFis: %s)" % (infra or "vazio")


def cluster(rows, radius=30.0):
    """Agrupa ERBs co-localizadas em sites físicos (grade + raio)."""
    cell = radius / 111000.0 * 2
    grid = defaultdict(list)
    sites = []
    for r in rows:
        key = (int(r["lat"] / cell), int(r["lng"] / cell))
        placed = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for s in grid[(key[0]+dx, key[1]+dy)]:
                    if haversine(r["lat"], r["lng"], s["lat"], s["lng"]) <= radius:
                        s["rows"].append(r); placed = True; break
                if placed: break
            if placed: break
        if not placed:
            s = {"lat": r["lat"], "lng": r["lng"], "rows": [r]}
            grid[key].append(s); sites.append(s)
    out = []
    for s in sites:
        ops = sorted({x["operadora"].upper() for x in s["rows"]})
        infras = sorted({x["infra"] for x in s["rows"] if x["infra"]})
        tecs = sorted({t for x in s["rows"] for t in x["tecs"].replace("-", " ").split()})
        r0 = s["rows"][0]
        blob = norm(" ".join(infras))
        has_rt, has_gf = "rooftop" in blob, "greenfield" in blob
        if has_rt and has_gf:
            tr = "Mista (verificar em campo) — GF+RT"
        elif has_rt:
            tr = TRILHA["rooftop"]
        elif has_gf:
            tr = TRILHA["greenfield"]
        else:
            tr = "indefinido (ClassInfraFis: %s)" % (" / ".join(infras) or "vazio")
        out.append({"lat": s["lat"], "lng": s["lng"], "operadoras": ops,
                    "tenancy": len(ops), "infra": " / ".join(infras) or "vazio",
                    "trilha": tr,
                    "tecs": " ".join(tecs), "uf": r0["uf"], "mun": r0["mun"],
                    "bairro": r0["bairro"], "logradouro": r0["logradouro"],
                    "estacoes": [x["estacao"] for x in s["rows"]],
                    "maps": f"https://maps.google.com/?q={s['lat']},{s['lng']}"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--near"); ap.add_argument("--radius", type=float, default=300.0)
    ap.add_argument("--estacao"); ap.add_argument("--mun"); ap.add_argument("--bairro")
    ap.add_argument("--addr"); ap.add_argument("--operadora"); ap.add_argument("--uf")
    ap.add_argument("--cluster", action="store_true")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not any([a.near, a.estacao, a.mun, a.bairro, a.addr, a.operadora, a.uf]):
        ap.error("informe ao menos um filtro (--near / --estacao / --mun / --addr ...)")

    lat = lng = None
    if a.near:
        lat, lng = (float(x) for x in a.near.split(","))

    hits = []
    for r in load(a.base):
        if a.estacao and r["estacao"] != a.estacao.strip(): continue
        if a.uf and norm(r["uf"]) != norm(a.uf): continue
        if a.mun and norm(a.mun) not in norm(r["mun"]): continue
        if a.bairro and norm(a.bairro) not in norm(r["bairro"]): continue
        if a.addr and norm(a.addr) not in norm(r["logradouro"]): continue
        if a.operadora and norm(a.operadora) not in norm(r["operadora"]): continue
        if lat is not None:
            d = haversine(lat, lng, r["lat"], r["lng"])
            if d > a.radius: continue
            r["dist_m"] = round(d)
        r["trilha"] = trilha(r["infra"])
        r["maps"] = f"https://maps.google.com/?q={r['lat']},{r['lng']}"
        hits.append(r)

    if lat is not None:
        hits.sort(key=lambda r: r.get("dist_m", 0))

    data = cluster(hits) if a.cluster else hits
    total = len(data)
    data = data[:a.limit]

    if a.json:
        print(json.dumps({"total": total, "exibidos": len(data),
                          "resultados": data}, ensure_ascii=False, indent=1))
        return

    print(f"# {total} resultado(s)" + (f" (exibindo {len(data)})" if total > len(data) else ""))
    for r in data:
        if a.cluster:
            print(f"\nSITE {r['lat']:.6f},{r['lng']:.6f} — tenancy {r['tenancy']} "
                  f"({', '.join(r['operadoras'])})\n  infra: {r['infra']} -> {r['trilha']}"
                  f"\n  tec: {r['tecs']} | {r['mun']}/{r['uf']} — {r['bairro']} — "
                  f"{r['logradouro']}\n  estações: {', '.join(r['estacoes'])}\n  {r['maps']}")
        else:
            d = f" | {r['dist_m']} m" if "dist_m" in r else ""
            print(f"\nEstação {r['estacao']} — {r['operadora']} — {r['mun']}/{r['uf']}{d}"
                  f"\n  {r['bairro']} — {r['logradouro']}"
                  f"\n  infra: {r['infra'] or 'vazio'} -> {r['trilha']} | tec: {r['tecs']} | faixa: {r['faixa']}"
                  f"\n  {r['lat']},{r['lng']}  {r['maps']}")


if __name__ == "__main__":
    main()
