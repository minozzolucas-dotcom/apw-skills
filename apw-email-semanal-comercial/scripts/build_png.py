#!/usr/bin/env python3
"""
Renderiza os dois PNGs do e-mail semanal comercial da APW Brasil.

    python3 build_png.py data.json <dir_saida>

Saidas:
    APW_KPIs_semana_mes_ano_<DD-MM-AAAA>.png
    APW_KPIs_por_diretor_<DD-MM-AAAA>.png

Pillow puro, sem navegador. Supersampling 2x + LANCZOS.
Schema do data.json: ver references/data.exemplo.json
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------- marca (apw-brand) ----------
NAVY = (1, 43, 94)        # #012B5E
AZUL = (28, 117, 187)     # #1C75BB
SAGE = (145, 165, 164)    # #91A5A4
VERDE = (0, 152, 119)     # #009877
OLIVA = (167, 175, 0)     # #A7AF00
CINZA = (93, 93, 93)      # #5D5D5D
WHITE = (255, 255, 255)
BG1 = (244, 247, 250)
BG2 = (238, 242, 246)
LINE = (219, 228, 238)

S = 2  # supersampling
W = 1300

# Liberation Sans = metricamente compativel com Arial (fonte oficial APW)
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
if not os.path.exists(FR):  # fallback DejaVu
    FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def f(size, bold=False):
    return ImageFont.truetype(FB if bold else FR, int(size * S))


class Canvas:
    def __init__(self, height):
        self.img = Image.new("RGB", (W * S, height * S), WHITE)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x, y, w, h, fill=None, outline=None, width=1):
        self.d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                         fill=fill, outline=outline, width=width * S)

    def text(self, x, y, s, font, fill=(0, 0, 0), anchor="la"):
        self.d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)

    def hline(self, x1, x2, y, fill=LINE, width=1):
        self.d.line([(x1 * S, y * S), (x2 * S, y * S)], fill=fill, width=width * S)

    def vline(self, x, y1, y2, fill=WHITE, width=1):
        self.d.line([(x * S, y1 * S), (x * S, y2 * S)], fill=fill, width=width * S)

    def tw(self, s, font):
        return self.d.textlength(s, font=font) / S

    def save(self, path, y_end):
        im = self.img.crop((0, 0, W * S, int(y_end * S)))
        im = im.resize((W, int(y_end)), Image.LANCZOS)
        im.save(path)
        return im.size


def header(c, titulo, referencia):
    c.rect(0, 0, W, 96, fill=NAVY)
    c.text(48, 30, "APW", f(30, True), WHITE)
    wm = c.tw("APW", f(30, True))
    c.text(48 + wm + 3, 30, "Brasil", f(30), SAGE)
    c.text(W - 48, 26, titulo, f(19, True), WHITE, anchor="ra")
    c.text(W - 48, 56, f"Fonte: Dynamics 365  ·  posição em {referencia}",
           f(14), SAGE, anchor="ra")
    c.rect(0, 96, W, 5, fill=AZUL)


def rodape(c, y, legenda):
    c.text(48, y, "APWireless Brasil Invest. Imob. LTDA", f(12), SAGE)
    c.text(W - 48, y, legenda, f(12), SAGE, anchor="ra")
    return y + 34


def fmt(v):
    """Numeros no padrao BR; None vira travessao."""
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:,.0f}".replace(",", ".")
    if isinstance(v, int):
        return f"{v:,}".replace(",", ".")
    return str(v)


def desafio(dt):
    """A conta que da sentido ao e-mail."""
    faltam = max(0, dt["meta_ano_deals"] - dt["totais"]["ano"]["deals"])
    meses = max(1, dt["meses_restantes"])
    ndir = max(1, dt["n_diretores"])
    return {
        "faltam": faltam,
        "por_mes": faltam / meses,
        "por_diretor": faltam / ndir,
        "por_dir_mes": faltam / ndir / meses,
        "meses": meses,
        "ndir": ndir,
    }


# =====================================================================
# PNG 1 — CONSOLIDADO (semana / mes / ano)
# =====================================================================
ROTULOS = [
    ("s1", "Qualificações (Stage 1)"),
    ("s3", "Propostas (Stage 3)"),
    ("s5", "Contratos (Stage 5)"),
    ("s8", "Submissions (Stage 8)"),
    ("s99", "Fechamentos (Stage 99)"),
]


def build_consolidado(dt, out):
    c = Canvas(1200)
    header(c, "KPIs COMERCIAIS — BRASIL", dt["referencia"])

    TOP = 138
    COL_W, GAP = 606, 40
    LX, RX = 48, 48 + COL_W + GAP
    RH = 44

    def bloco(x, titulo, sub, vals):
        y = TOP
        c.text(x, y, titulo, f(20, True), NAVY)
        c.text(x + COL_W, y + 4, sub, f(14), CINZA, anchor="ra")
        y += 34
        c.rect(x, y, COL_W, 40, fill=NAVY)
        c.text(x + 18, y + 12, "ETAPA DO FUNIL", f(14, True), WHITE)
        c.text(x + COL_W - 18, y + 12, "MOVIMENTOS", f(14, True), WHITE, anchor="ra")
        y += 40
        tot = 0
        for i, (k, lbl) in enumerate(ROTULOS):
            v = vals.get(k)
            c.rect(x, y, COL_W, RH, fill=BG1 if i % 2 == 0 else WHITE)
            c.hline(x, x + COL_W, y + RH)
            c.text(x + 18, y + 13, lbl, f(16), (0, 0, 0))
            cor = OLIVA if k == "s8" else (VERDE if k == "s99" else NAVY)
            c.text(x + COL_W - 18, y + 11, fmt(v), f(19, True), cor, anchor="ra")
            tot += v or 0
            y += RH
        c.rect(x, y, COL_W, 46, fill=BG2)
        c.rect(x, y, COL_W, 46, outline=AZUL, width=2)
        c.text(x + 18, y + 14, f"TOTAL DE MOVIMENTOS ({titulo})", f(15, True), NAVY)
        c.text(x + COL_W - 18, y + 12, fmt(tot), f(20, True), AZUL, anchor="ra")
        return y + 46

    jan = dt["janelas"]
    tt = dt["totais"]
    b1 = bloco(LX, "SEMANA", jan["semana"], tt["semana"])
    b2 = bloco(RX, "MÊS", jan["mes"], tt["mes"])

    # ---- ANO ----
    y = max(b1, b2) + 42
    c.text(48, y, "ANO — ACUMULADO", f(20, True), NAVY)
    c.text(W - 48, y + 4, jan["ano"], f(14), CINZA, anchor="ra")
    y += 34

    a = tt["ano"]

    def faixa(y, itens, h, destaque):
        """Card faltando some e os demais reflowam. Card vazio com travessão
        não informa nada e ainda sugere que o dado é zero — pior que ausência."""
        itens = [(l, v, k) for l, v, k in itens if v is not None]
        if not itens:
            return y
        cw = (W - 96 - (len(itens) - 1) * 18) / len(itens)
        for i, (lbl, val, cor) in enumerate(itens):
            x = 48 + i * (cw + 18)
            if destaque:
                c.rect(x, y, cw, h, fill=BG1)
                c.rect(x, y, 5, h, fill=cor)
                c.text(x + 22, y + 20, lbl, f(13, True), CINZA)
                c.text(x + 22, y + 44, val, f(32, True), cor)
            else:
                c.rect(x, y, cw, h, fill=WHITE, outline=LINE, width=1)
                c.text(x + 22, y + 15, lbl, f(12, True), CINZA)
                c.text(x + 22, y + 33, val, f(24, True), cor)
        return y + h + 18

    def nn(v, suf=""):
        return None if v is None else fmt(v) + suf

    y = faixa(y, [
        ("DEALS FECHADOS", nn(a.get("deals")), VERDE),
        ("% DA META ANUAL", nn(a.get("pct"), "%"), OLIVA),
        ("VALOR ADQUIRIDO", nn(a.get("adquirido")), NAVY),
        ("META ANUAL", nn(a.get("meta")), CINZA),
    ], 96, True)

    y = faixa(y, [
        ("LEASES", nn(a.get("leases")), NAVY),
        ("PIPELINE (VALOR)", nn(a.get("pipeline")), AZUL),
        ("HOT DEALS NO PIPELINE", nn(dt.get("hot_deals")), AZUL),
        ("SUBMISSIONS NO MÊS", nn(tt["mes"].get("s8")), OLIVA),
    ], 70, False)
    y += 22

    # ---- DESAFIO ----
    ds = desafio(dt)
    c.rect(48, y, W - 96, 148, fill=NAVY)
    c.text(74, y + 22, dt.get("titulo_desafio",
           "DESAFIO ATÉ DEZEMBRO — FECHAR O ANO EM 3 DÍGITOS"), f(18, True), WHITE)
    c.hline(74, W - 74, y + 54, AZUL, 2)
    metr = [
        ("META", f"{dt['meta_ano_deals']} deals"),
        ("FALTAM", f"{ds['faltam']} deals"),
        ("MESES", str(ds["meses"])),
        ("POR MÊS", f"{ds['por_mes']:.1f}".replace(".", ",") + " deals"),
        ("DIRETORES", str(ds["ndir"])),
        ("POR DIRETOR", f"{ds['por_diretor']:.1f}".replace(".", ",") + " deals"),
    ]
    MW = (W - 96 - 52) / 6
    for i, (lbl, val) in enumerate(metr):
        x = 74 + i * MW
        c.text(x, y + 74, lbl, f(12, True), SAGE)
        c.text(x, y + 94, val, f(22, True), WHITE)
    y += 148 + 26

    y = rodape(c, y, "Stage 1 = qualificação · Stage 3 = proposta · Stage 5 = contrato · "
                     "Stage 8 = submission · Stage 99 = fechamento")
    return c.save(out, y)


# =====================================================================
# PNG 2 — POR DIRETOR
# =====================================================================
def build_por_diretor(dt, out):
    dirs = sorted(dt["diretores"], key=lambda x: (-x["ano"]["deals"], x["nome"]))
    n = len(dirs)
    c = Canvas(420 + n * 40 + 300)
    header(c, "KPIs POR DIRETOR DE AQUISIÇÃO — BRASIL", dt["referencia"])

    X0 = 48
    CN = 268                  # coluna do nome
    CS = CM = 60              # colunas de estagio
    CD, CV, CP = 78, 150, 96  # colunas do ano

    # A semana omite Stage 8: o CRM nao atribui submission por diretor na janela curta.
    HS = ["s1", "s3", "s5", "s99"]
    HM = ["s1", "s3", "s5", "s8", "s99"]
    LS = ["S1", "S3", "S5", "FECH"]
    LM = ["S1", "S3", "S5", "SUB", "FECH"]

    xs_sem = X0 + CN
    xs_mes = xs_sem + len(HS) * CS
    xs_ano = xs_mes + len(HM) * CM
    TW = CN + len(HS) * CS + len(HM) * CM + CD + CV + CP

    y = 132
    c.text(X0, y, "DESEMPENHO POR DIRETOR", f(20, True), NAVY)
    c.text(X0 + TW, y + 4, f"{n} diretores  ·  ordenado por deals fechados no ano",
           f(14), CINZA, anchor="ra")
    y += 34

    # faixa de grupos
    c.rect(X0, y, TW, 30, fill=AZUL)
    c.text(X0 + 16, y + 8, "DIRETOR", f(13, True), WHITE)
    c.text(xs_sem + len(HS) * CS / 2, y + 8, f"SEMANA  {dt['janelas']['semana']}",
           f(13, True), WHITE, anchor="ma")
    c.text(xs_mes + len(HM) * CM / 2, y + 8, f"MÊS  {dt['janelas']['mes']}",
           f(13, True), WHITE, anchor="ma")
    c.text(xs_ano + (CD + CV + CP) / 2, y + 8, "ANO — ACUMULADO",
           f(13, True), WHITE, anchor="ma")
    for xd in (xs_sem, xs_mes, xs_ano):
        c.vline(xd, y, y + 30, WHITE, 2)
    y += 30

    # cabecalho de colunas
    HH = 34
    c.rect(X0, y, TW, HH, fill=NAVY)
    for i, h in enumerate(LS):
        c.text(xs_sem + i * CS + CS - 12, y + 10, h, f(13, True), WHITE, anchor="ra")
    for i, h in enumerate(LM):
        c.text(xs_mes + i * CM + CM - 12, y + 10, h, f(13, True), WHITE, anchor="ra")
    c.text(xs_ano + CD - 12, y + 10, "DEALS", f(13, True), WHITE, anchor="ra")
    c.text(xs_ano + CD + CV - 12, y + 10, "ADQUIRIDO", f(13, True), WHITE, anchor="ra")
    c.text(xs_ano + CD + CV + CP - 12, y + 10, "% META", f(13, True), WHITE, anchor="ra")
    y += HH

    RH = 38

    def cell(x, w, yy, val, bold=False, cor=(0, 0, 0), size=15):
        # zero vira travessao sage: a linha fica legivel, o olho vai no que tem numero
        s = "–" if (isinstance(val, int) and val == 0) or val is None else fmt(val)
        c.text(x + w - 12, yy + (RH - size * 1.35) / 2 + 1, s,
               f(size, bold), SAGE if s == "–" else cor, anchor="ra")

    for i, dr in enumerate(dirs):
        c.rect(X0, y, TW, RH, fill=BG1 if i % 2 == 0 else WHITE)
        c.hline(X0, X0 + TW, y + RH)
        c.text(X0 + 16, y + 11, dr["nome"], f(15, True), NAVY)
        for j, k in enumerate(HS):
            cell(xs_sem + j * CS, CS, y, dr["semana"].get(k),
                 bold=(k == "s99"), cor=VERDE if k == "s99" else (0, 0, 0))
        for j, k in enumerate(HM):
            cor = OLIVA if k == "s8" else (VERDE if k == "s99" else (0, 0, 0))
            cell(xs_mes + j * CM, CM, y, dr["mes"].get(k),
                 bold=(k in ("s8", "s99")), cor=cor)
        a = dr["ano"]
        cell(xs_ano, CD, y, a.get("deals"), bold=True, cor=NAVY, size=16)
        cell(xs_ano + CD, CV, y, a.get("adquirido"), cor=CINZA)
        pct = a.get("pct")
        if pct is not None:
            pc = SAGE if pct == 0 else (VERDE if pct >= 100 else (AZUL if pct >= 50 else OLIVA))
            c.text(xs_ano + CD + CV + CP - 12, y + 10, f"{pct}%", f(16, True), pc, anchor="ra")
        y += RH

    # ---- TOTAL ----
    tt = dt["totais"]
    c.rect(X0, y, TW, 44, fill=BG2)
    c.rect(X0, y, TW, 44, outline=AZUL, width=2)
    c.text(X0 + 16, y + 14, "TOTAL BRASIL", f(15, True), NAVY)
    for j, k in enumerate(HS):
        c.text(xs_sem + j * CS + CS - 12, y + 13, fmt(tt["semana"].get(k)),
               f(16, True), NAVY, anchor="ra")
    for j, k in enumerate(HM):
        c.text(xs_mes + j * CM + CM - 12, y + 13, fmt(tt["mes"].get(k)),
               f(16, True), NAVY, anchor="ra")
    a = tt["ano"]
    c.text(xs_ano + CD - 12, y + 13, fmt(a.get("deals")), f(17, True), AZUL, anchor="ra")
    c.text(xs_ano + CD + CV - 12, y + 13, fmt(a.get("adquirido")), f(16, True), AZUL, anchor="ra")
    if a.get("pct") is not None:
        c.text(xs_ano + CD + CV + CP - 12, y + 13, f"{a['pct']}%", f(17, True), AZUL, anchor="ra")
    y += 44 + 12

    obs = dt.get("obs")
    if obs:
        c.text(X0, y, obs, f(12), CINZA)
        y += 34

    # ---- DESAFIO ----
    ds = desafio(dt)
    c.rect(X0, y, TW, 132, fill=NAVY)
    c.text(X0 + 26, y + 20, dt.get("titulo_desafio_diretor",
           f"DESAFIO — {ds['faltam']} DEALS PARA FECHAR O ANO EM 3 DÍGITOS"),
           f(17, True), WHITE)
    c.hline(X0 + 26, X0 + TW - 26, y + 50, AZUL, 2)
    lo, hi = int(ds["por_diretor"]), int(ds["por_diretor"]) + 1
    metr = [
        ("POR DIRETOR", f"{lo} a {hi} deals"),
        ("POR DIRETOR/MÊS", f"{ds['por_dir_mes']:.1f}".replace(".", ",") + " deal"),
        ("TIME/MÊS", f"{ds['por_mes']:.1f}".replace(".", ",") + " deals"),
        ("HOT DEALS HOJE", fmt(dt.get("hot_deals"))),
        ("MESES RESTANTES", str(ds["meses"])),
    ]
    MW = (TW - 52) / len(metr)
    for i, (lbl, val) in enumerate(metr):
        x = X0 + 26 + i * MW
        c.text(x, y + 68, lbl, f(12, True), SAGE)
        c.text(x, y + 87, val, f(21, True), WHITE)
    y += 132 + 24

    y = rodape(c, y, "S1 = qualificação · S3 = proposta · S5 = contrato · "
                     "SUB = submission · FECH = fechamento")
    return c.save(out, y)


def conferir(dt):
    """Soma dos diretores x total. Devolve lista de avisos (nao aborta)."""
    avisos = []
    for jan, keys in (("semana", ["s1", "s3", "s5", "s99"]),
                      ("mes", ["s1", "s3", "s5", "s8", "s99"])):
        for k in keys:
            soma = sum((d[jan].get(k) or 0) for d in dt["diretores"])
            tot = dt["totais"][jan].get(k)
            if tot is not None and soma != tot:
                avisos.append(f"{jan}.{k}: diretores somam {soma}, total diz {tot}")
    soma = sum(d["ano"]["deals"] for d in dt["diretores"])
    tot = dt["totais"]["ano"]["deals"]
    if soma != tot:
        avisos.append(f"ano.deals: diretores somam {soma}, total diz {tot} "
                      f"(diferença de {tot - soma} = owners fora da lista/pool)")
    return avisos


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    dt = json.load(open(sys.argv[1], encoding="utf-8"))
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    stamp = dt["referencia"].replace("/", "-")

    for a in conferir(dt):
        print("AVISO:", a)

    p1 = os.path.join(outdir, f"APW_KPIs_semana_mes_ano_{stamp}.png")
    p2 = os.path.join(outdir, f"APW_KPIs_por_diretor_{stamp}.png")
    print("consolidado", build_consolidado(dt, p1), p1)
    print("por diretor", build_por_diretor(dt, p2), p2)

    ds = desafio(dt)
    print(f"desafio: faltam {ds['faltam']} · {ds['por_mes']:.1f}/mês · "
          f"{ds['por_diretor']:.1f}/diretor · {ds['por_dir_mes']:.1f}/diretor/mês")


if __name__ == "__main__":
    main()
