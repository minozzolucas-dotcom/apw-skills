#!/usr/bin/env python3
# =====================================================================
# APW Brasil — Reporte Diário de Produtividade do CRM (build)
#
# USO
#   python3 build_report.py data.json <saida> [YYYY-MM-DD]
#     data.json   -> esqueleto produzido por references/collection.js
#                    (+ destaque_dia / destaque_semana / leitura_dia já preenchidos)
#     <saida>      -> prefixo de saída (gera <saida>.html e <saida>.png)
#     [YYYY-MM-DD] -> dia-alvo p/ o pace do radar (default: data.alvo do json)
#
# SAÍDA
#   HTML + PNG na identidade APW Brasil (skill apw-brand). O PNG é o
#   entregável: o Lucas cola no corpo do e-mail (o Outlook zera cor de
#   texto ao colar HTML; a imagem preserva a marca 100%).
#
# PNG: playwright (chromium via /opt/google/chrome/chrome) -> fallback
#      chrome headless subprocess. Requer `pip install playwright`.
# =====================================================================
import sys, os, json, shutil, subprocess, html as _html
from datetime import date, datetime

# ---- 13 diretores Brasil (Bruna Matos removida 24/07/2026). Ao entrar/sair
#      diretor, mexer AQUI e na lista NM do collection.js. ----
N_DIR = 13

# ---- paleta oficial APW (skill apw-brand) ----
BRAND = {
    "navy":  "#012B5E",
    "azul":  "#1C75BB",
    "sage":  "#91A5A4",
    "verde": "#009877",
    "oliva": "#A7AF00",
    "cinza": "#5D5D5D",
    "bg":    "#f4f7fa",
    "bg2":   "#eef2f6",
    "line":  "#dbe4ee",
    "olivabg": "#FBFBEF",
    "white": "#FFFFFF",
}
RAZAO = "APWireless Brasil Invest. Imob. LTDA"

# ---- metas por diretor / semana (SKILL.md) ----
META = {"s1": 3, "s3": 2, "rep": 4, "ativ": 100, "subst_pct": 35}


def esc(s):
    return _html.escape(str(s if s is not None else ""))


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pace_marker(decorridos, total):
    """fração da semana já decorrida (dias úteis)."""
    total = total or 5
    return max(0.0, min(1.0, (decorridos or 0) / total))


def radar_bloco(data, pace):
    """radar de time: total semana vs meta semanal do time, com marcador de ritmo."""
    b = BRAND
    tot_sem = data["totais"]["semana"]
    n = data.get("n_diretores", N_DIR) or N_DIR
    metas_time = {"s1": META["s1"] * n, "s3": META["s3"] * n,
                  "rep": META["rep"] * n, "ativ": META["ativ"] * n}
    rotulos = {"s1": "Stage 1", "s3": "Stage 3", "rep": "Repropostas", "ativ": "Atividades"}
    linhas = []
    for k in ["s1", "s3", "rep", "ativ"]:
        atual = tot_sem.get(k, 0)
        meta = metas_time[k] or 1
        esperado = pace * meta                       # ritmo esperado até hoje
        no_ritmo = atual >= esperado
        cor = b["verde"] if no_ritmo else b["oliva"]
        pct = max(0.0, min(1.0, atual / meta))
        pct_pace = max(0.0, min(1.0, esperado / meta))
        tag = "no ritmo" if no_ritmo else "atrás do ritmo"
        linhas.append(f"""
        <tr>
          <td style="padding:6px 10px;font:bold 13px Arial;color:{b['navy']};white-space:nowrap">{rotulos[k]}</td>
          <td style="padding:6px 10px;width:100%">
            <div style="position:relative;height:16px;background:{b['bg2']};border-radius:8px;overflow:hidden">
              <div style="position:absolute;left:0;top:0;height:16px;width:{pct*100:.1f}%;background:{cor};border-radius:8px"></div>
              <div style="position:absolute;left:{pct_pace*100:.1f}%;top:-2px;height:20px;width:2px;background:{b['navy']}" title="ritmo esperado"></div>
            </div>
          </td>
          <td style="padding:6px 10px;font:13px Arial;color:{b['cinza']};white-space:nowrap;text-align:right">
            <b style="color:{cor}">{atual}</b> / {meta} &nbsp;<span style="color:{cor};font-size:11px">({tag})</span>
          </td>
        </tr>""")
    return f"""
    <div style="border:1px solid {b['line']};border-radius:10px;overflow:hidden;margin:0 0 18px">
      <div style="background:{b['navy']};color:#fff;font:bold 13px Arial;padding:8px 12px">
        Radar do time — semana ({esc(data.get('semana_janela',''))}) · ritmo {data['dias_uteis']['decorridos']}/{data['dias_uteis']['total']} dias úteis
      </div>
      <table style="border-collapse:collapse;width:100%">{''.join(linhas)}</table>
      <div style="font:11px Arial;color:{b['sage']};padding:6px 12px;border-top:1px solid {b['line']}">
        Barra = acumulado do time na semana · marcador vertical = ritmo esperado até hoje · meta/diretor: S1 {META['s1']} · S3 {META['s3']} · Repropostas {META['rep']} · Atividades {META['ativ']}.
      </div>
    </div>"""


def subst_bar(subst, ativ):
    """barra de substantivas com marcador da meta 35%."""
    b = BRAND
    pct = (subst / ativ) if ativ else 0.0
    pct = max(0.0, min(1.0, pct))
    alvo = META["subst_pct"] / 100.0
    ok = pct >= alvo
    cor = b["verde"] if ok else b["oliva"]
    return f"""<div style="position:relative;height:12px;background:{b['bg2']};border-radius:6px;overflow:hidden;min-width:90px">
      <div style="position:absolute;left:0;top:0;height:12px;width:{pct*100:.0f}%;background:{cor};border-radius:6px"></div>
      <div style="position:absolute;left:{alvo*100:.0f}%;top:-1px;height:14px;width:2px;background:{b['navy']}"></div>
    </div>
    <div style="font:11px Arial;color:{cor};text-align:center;margin-top:2px">{pct*100:.0f}%</div>"""


def cel_num(v, hoje=False):
    b = BRAND
    cor = b["azul"] if (hoje and v) else b["navy"]
    peso = "bold" if v else "normal"
    txt = str(v) if v else "·"
    return f'<td style="padding:6px 8px;text-align:center;font:{peso} 13px Arial;color:{cor}">{txt}</td>'


def lnums_bloco(d):
    """L-numbers movidos por diretor (azul = hoje)."""
    b = BRAND
    ls_dia = d.get("ls", {}).get("dia", {}) or {}
    ls_sem = d.get("ls", {}).get("semana", {}) or {}
    hoje = set()
    for k in ("s1", "s3", "rep"):
        for L in ls_dia.get(k, []) or []:
            if L:
                hoje.add(str(L))
    todos = []
    seen = set()
    for k in ("s1", "s3", "rep"):
        for L in (ls_sem.get(k, []) or []):
            if L and str(L) not in seen:
                seen.add(str(L))
                todos.append(str(L))
    if not todos:
        return ""
    chips = []
    for L in todos:
        if L in hoje:
            chips.append(f'<span style="color:{b["azul"]};font-weight:bold">{esc(L)}</span>')
        else:
            chips.append(f'<span style="color:{b["cinza"]}">{esc(L)}</span>')
    return f'<div style="font:11px Arial;padding:2px 8px 8px 8px;color:{b["cinza"]}">{" · ".join(chips)}</div>'


def tabela_diretores(data):
    b = BRAND
    head_cols = "".join(
        f'<th style="padding:6px 8px;font:bold 11px Arial;color:#fff;background:{b["azul"]}">{c}</th>'
        for c in ["S1", "S3", "Rep", "Ativ"]
    )
    thead = f"""
      <tr>
        <th style="padding:8px 10px;text-align:left;font:bold 12px Arial;color:#fff;background:{b['navy']}">Diretor</th>
        <th colspan="4" style="padding:6px;font:bold 11px Arial;color:#fff;background:{b['navy']}">HOJE ({esc(data.get('dia',''))})</th>
        <th colspan="4" style="padding:6px;font:bold 11px Arial;color:#fff;background:{b['navy']}">SEMANA</th>
        <th style="padding:6px 8px;font:bold 11px Arial;color:#fff;background:{b['navy']}">Subst. (sem)</th>
      </tr>
      <tr>
        <th style="background:{b['azul']}"></th>{head_cols}{head_cols}
        <th style="padding:6px 8px;font:bold 11px Arial;color:#fff;background:{b['azul']}">meta 35%</th>
      </tr>"""
    linhas = []
    zebra = False
    for d in data["diretores"]:
        zebra = not zebra
        bg = b["white"] if zebra else b["bg"]
        dia = d.get("dia", {}) or {}
        sem = d.get("semana", {}) or {}
        cells = (
            cel_num(dia.get("s1", 0), True) + cel_num(dia.get("s3", 0), True) +
            cel_num(dia.get("rep", 0), True) + cel_num(dia.get("ativ", 0), True) +
            cel_num(sem.get("s1", 0)) + cel_num(sem.get("s3", 0)) +
            cel_num(sem.get("rep", 0)) + cel_num(sem.get("ativ", 0))
        )
        subst = f'<td style="padding:6px 8px;width:120px">{subst_bar(sem.get("subst",0), sem.get("ativ",0))}</td>'
        linhas.append(f"""
        <tr style="background:{bg}">
          <td style="padding:6px 10px;font:bold 12px Arial;color:{b['navy']};white-space:nowrap;border-left:3px solid {b['sage']}">{esc(d['nome'])}</td>
          {cells}{subst}
        </tr>
        <tr style="background:{bg}"><td colspan="10">{lnums_bloco(d)}</td></tr>""")
    return f"""
    <table style="border-collapse:collapse;width:100%;border:1px solid {b['line']};border-radius:10px;overflow:hidden">
      <thead>{thead}</thead>
      <tbody>{''.join(linhas)}</tbody>
    </table>"""


def destaque_card(titulo, txt):
    b = BRAND
    if not txt:
        return ""
    return f"""
    <div style="flex:1;background:{b['olivabg']};border:1px solid {b['line']};border-radius:10px;padding:10px 14px">
      <div style="font:bold 11px Arial;color:{b['sage']};text-transform:uppercase;letter-spacing:.5px">{esc(titulo)}</div>
      <div style="font:13px Arial;color:{b['navy']};margin-top:3px">{esc(txt)}</div>
    </div>"""


def destaque_texto(d):
    """aceita string ou {nome, texto}."""
    if not d:
        return ""
    if isinstance(d, str):
        return d
    nome = d.get("nome", "")
    txt = d.get("texto", d.get("linha", ""))
    return (f"{nome} — {txt}" if nome and txt else (nome or txt))


def build_html(data):
    b = BRAND
    pace = pace_marker(data["dias_uteis"]["decorridos"], data["dias_uteis"]["total"])
    wordmark = (f'<span style="font-weight:bold;color:#fff">APW</span>'
                f'<span style="color:{b["sage"]}">Brasil</span>')
    dd = destaque_card("Destaque do dia", destaque_texto(data.get("destaque_dia")))
    ds = destaque_card("Destaque da semana", destaque_texto(data.get("destaque_semana")))
    destaques = ""
    if dd or ds:
        destaques = f'<div style="display:flex;gap:12px;margin:0 0 18px">{dd}{ds}</div>'
    leitura = ""
    if (data.get("leitura_dia") or "").strip():
        leitura = f"""
        <div style="border-left:3px solid {b['azul']};background:{b['bg2']};padding:10px 14px;border-radius:0 8px 8px 0;margin-top:18px">
          <div style="font:bold 11px Arial;color:{b['azul']};text-transform:uppercase;letter-spacing:.5px">Leitura do dia</div>
          <div style="font:13px Arial;color:{b['navy']};margin-top:3px">{esc(data['leitura_dia'])}</div>
        </div>"""
    corte = ""
    if data.get("corte_hora"):
        try:
            ch = datetime.fromisoformat(data["corte_hora"].replace("Z", "+00:00"))
            corte = ch.strftime(" · corte %d/%m %H:%MZ")
        except Exception:
            pass
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{background:{b['bg']};font-family:Arial,'Liberation Sans',sans-serif}}</style>
</head><body>
<div class="wrap" style="width:1080px;background:#fff;margin:0 auto;border:1px solid {b['line']};border-radius:14px;overflow:hidden">
  <div style="background:{b['navy']};padding:16px 22px;display:flex;justify-content:space-between;align-items:center">
    <div style="font:22px Arial">{wordmark}</div>
    <div style="text-align:right;color:#fff">
      <div style="font:bold 15px Arial">Reporte Diário de Produtividade</div>
      <div style="font:12px Arial;color:{b['sage']}">CRM Dynamics 365 Brasil · {esc(data.get('referencia',''))}{corte}</div>
    </div>
  </div>
  <div style="height:4px;background:{b['azul']}"></div>
  <div style="padding:20px 22px">
    {radar_bloco(data, pace)}
    {destaques}
    {tabela_diretores(data)}
    {leitura}
  </div>
  <div style="background:{b['bg2']};border-top:1px solid {b['line']};padding:10px 22px;font:11px Arial;color:{b['sage']};text-align:center">
    {esc(RAZAO)} · {N_DIR} diretores de aquisição · gerado {datetime.now().strftime('%d/%m/%Y %H:%M')}
  </div>
</div>
</body></html>"""


def html_to_png(html_path, png_path):
    """playwright -> chrome headless subprocess. True se gerou PNG."""
    try:
        from playwright.sync_api import sync_playwright
        chrome = None
        for p in ["/opt/google/chrome/chrome", shutil.which("google-chrome"),
                  shutil.which("chromium"), shutil.which("chromium-browser")]:
            if p and os.path.exists(p):
                chrome = p
                break
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
    for exe in ["/opt/google/chrome/chrome", shutil.which("google-chrome"),
                shutil.which("chromium"), shutil.which("chromium-browser")]:
        if exe and os.path.exists(exe):
            try:
                subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu",
                                "--window-size=1120,1600", f"--screenshot={png_path}",
                                "file://" + os.path.abspath(html_path)],
                               check=True, timeout=60,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(png_path):
                    return True
            except Exception as e:
                print("  [png via", exe, "falhou]", e)
    return False


def main():
    if len(sys.argv) < 3:
        print("uso: python3 build_report.py data.json <saida> [YYYY-MM-DD]")
        sys.exit(1)
    data_path, saida = sys.argv[1], sys.argv[2]
    data = load(data_path)
    # 3º arg opcional: dia-alvo (o pace do radar recalcula sozinho via dias_uteis do json)
    if len(sys.argv) >= 4 and sys.argv[3]:
        data["alvo"] = sys.argv[3]

    if data.get("n_diretores") and data["n_diretores"] != N_DIR:
        print(f"  [aviso] n_diretores={data['n_diretores']} difere de N_DIR={N_DIR} "
              f"(build). Conferir a lista de diretores nos DOIS arquivos.")

    html = build_html(data)
    html_path = saida + ".html"
    png_path = saida + ".png"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML:", html_path)

    if html_to_png(html_path, png_path):
        print("PNG: ", png_path)
    else:
        print("PNG NÃO gerado — verifique playwright/chrome. HTML disponível para render manual.")


if __name__ == "__main__":
    main()
