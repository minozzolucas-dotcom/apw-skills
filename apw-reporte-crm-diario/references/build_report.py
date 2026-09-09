"""
build_report.py — Reporte Diário CRM Brasil (APW) — formato oficial
Paleta: navy #012B5E, azul #1C75BB, verde #009877, oliva #A7AF00, vermelho #C0392B
Largura 900px. Aceita formato novo (diretores[]) ou antigo (directors{}).
uso: python3 build_report.py <data.json> <pasta_saida> <YYYY-MM-DD>
"""
import json, sys, html as _html, math
from datetime import datetime, date
from pathlib import Path

N_DIR=14; RAZAO="APWireless Brasil Invest. Imob. LTDA"
NAVY="#012B5E"; AZUL="#1C75BB"; VERDE="#009877"; OLIVA="#A7AF00"; RED="#C0392B"
SAGE="#91A5A4"; CINZA="#5D5D5D"; BG="#ffffff"; BG2="#f7fafc"; BG3="#f4f7fa"
BG4="#fbfcfe"; LINE="#dce4ec"; BAR_BG="#e6ecf2"; BAR_ZERO="#cfd8e3"; NAVY2="#0a3a72"
HBDR="#dbe4ee"

def e(t): return _html.escape((t or "").strip())
def pct(a,b): return round(100*a/b) if b else 0

def _normalize(d):
    if "directors" in d and "mov" in d:
        d.setdefault("semana_janela", ""); d.setdefault("dias_uteis",{})
        d.setdefault("metas",{}); d.setdefault("totais",{}); d.setdefault("n_diretores",N_DIR)
        d.setdefault("corte_hora",""); return d
    out={"date":d.get("alvo") or d.get("date"),"directors":{},"dia":{"s1":[],"s3":[],"rep":[]},"mov":{},
         "semana_janela":d.get("semana_janela",""),"dias_uteis":d.get("dias_uteis",{}),
         "metas":d.get("metas",{}),"totais":d.get("totais",{}),"n_diretores":d.get("n_diretores",N_DIR),
         "corte_hora":d.get("corte_hora","")}
    dd,ds=d.get("destaque_dia"),d.get("destaque_semana")
    if isinstance(dd,dict): out["destaque_dia"]=f'{dd.get("nome","")} — {dd.get("fatos","")}.'
    elif isinstance(dd,str): out["destaque_dia"]=dd
    if isinstance(ds,dict): out["destaque_semana"]=f'{ds.get("nome","")} — {ds.get("fatos","")}.'
    elif isinstance(ds,str): out["destaque_semana"]=ds
    for it in d.get("diretores",[]):
        nm=it["nome"]; ls_d=(it.get("ls") or {}).get("dia") or {}; ls_s=(it.get("ls") or {}).get("semana") or {}
        out["directors"][nm]={"s1":it["semana"]["s1"],"s3":it["semana"]["s3"],"rep":it["semana"]["rep"],
                              "tot":it["semana"]["ativ"],"totD":it["dia"]["ativ"],
                              "sub":it["semana"]["subst"],"subD":it["dia"]["subst"]}
        for L in ls_d.get("s1",[]): out["dia"]["s1"].append([nm,L])
        for L in ls_d.get("s3",[]): out["dia"]["s3"].append([nm,L])
        for L in ls_d.get("rep",[]): out["dia"]["rep"].append([nm,L])
        mov={}
        for k in ("s1","s3","rep"):
            sl=ls_s.get(k,[]); td=set(ls_d.get(k,[]))
            if sl: mov[k]=[[L,1 if L in td else 0] for L in sl]
        if mov: out["mov"][nm]=mov
    return out

def radar_bar(val, meta, ritmo_val, width=210):
    pp=min(val/meta,1.0) if meta else 0
    pr=min(ritmo_val/meta,1.0) if meta else 0
    color=VERDE if val>=ritmo_val else (OLIVA if val>=ritmo_val*0.5 else RED)
    return (f'<div style="position:relative;width:{width}px;height:14px;background:{BAR_BG};border-radius:7px;display:inline-block;vertical-align:middle;">'
            f'<div style="position:absolute;left:{pr*100:.1f}%;top:-3px;width:2px;height:20px;background:{NAVY};"></div>'
            f'<div style="width:{pp*100:.8f}%;height:14px;background:{color};border-radius:7px;"></div></div>')

def mini_bar_cell(val, meta, align_center=True):
    pp=min(val/meta,1.0) if meta else 0
    color=VERDE if val>=meta else (OLIVA if val>0 else BAR_ZERO)
    num_color=VERDE if val>=meta else NAVY
    bar=(f'<div style="margin:2px auto 0;width:42px;height:8px;background:{BAR_BG};border-radius:4px;">'
         f'<div style="width:{pp*100:.1f}%;height:8px;background:{color};border-radius:4px;"></div></div>')
    return (f'<td align="center" style="padding:6px 6px;border:1px solid {LINE};">'
            f'<div style="font-weight:bold;font-size:12px;color:{num_color};line-height:1.1;">{val}</div>{bar}</td>')

def subst_bar_cell(sp, spd):
    pp=min(sp/100,1.0); color=VERDE if sp>=35 else (OLIVA if sp>=20 else RED)
    bar=(f'<div style="position:relative;width:74px;height:11px;background:{BAR_BG};border-radius:6px;display:inline-block;vertical-align:middle;">'
         f'<div style="position:absolute;left:{min(35/100,1)*100:.0f}%;top:-2px;width:2px;height:15px;background:{SAGE};"></div>'
         f'<div style="width:{pp*100:.8f}%;height:11px;background:{color};border-radius:6px;"></div></div>')
    return (f'<td style="padding:7px 8px;border:1px solid {LINE};white-space:nowrap;">'
            f'{bar} <span style="font-size:11px;color:{NAVY};">{sp}%</span>'
            f' <span style="font-size:10px;color:{CINZA};">(dia {spd}%)</span></td>')

def main():
    data_raw=json.load(open(sys.argv[1]))
    out_dir=Path(sys.argv[2]); out_dir.mkdir(parents=True,exist_ok=True)
    alvo=sys.argv[3] if len(sys.argv)>3 else (data_raw.get("alvo") or date.today().isoformat())
    data=_normalize(data_raw)

    dt=datetime.strptime(alvo,"%Y-%m-%d")
    dias_pt=["segunda","terça","quarta","quinta","sexta","sábado","domingo"]
    data_fmt=f'{dias_pt[dt.weekday()]}, {dt.day:02d}/{dt.month:02d}/{dt.year}'

    metas=data.get("metas") or {}
    ms1=metas.get("s1",3); ms3=metas.get("s3",2); mrep=metas.get("repropostas",4)
    mativ=metas.get("atividades",100); msub=metas.get("substantivas_pct",35)
    du=data.get("dias_uteis") or {}; dec=du.get("decorridos",1); tdu=du.get("total",5)
    ritmo=dec/tdu if tdu else 0
    n=data.get("n_diretores",N_DIR)
    TM={"s1":ms1*n,"s3":ms3*n,"rep":mrep*n,"ativ":mativ*n}
    tot=data.get("totais",{}); totS=tot.get("semana",{}); totD=tot.get("dia",{})
    AW={"s1":totS.get("s1",0),"s3":totS.get("s3",0),"rep":totS.get("rep",0),"ativ":totS.get("ativ",0),"sub":totS.get("subst",0)}
    AD={"s1":totD.get("s1",0),"s3":totD.get("s3",0),"rep":totD.get("rep",0),"ativ":totD.get("ativ",0),"sub":totD.get("subst",0)}
    subw=pct(AW["sub"],AW["ativ"]); subd=pct(AD["sub"],AD["ativ"])
    semjan=data.get("semana_janela","")

    corte=data.get("corte_hora","")
    try:
        cd=datetime.fromisoformat(corte.replace("Z","+00:00"))
        cs=f'{cd.day:02d}/{cd.month:02d} {cd.hour:02d}:{cd.minute:02d}Z'
    except: cs=corte[:16] if corte else ""

    md_s1=math.ceil(ms1*n/tdu); md_s3=math.ceil(ms3*n/tdu)
    md_rep=math.ceil(mrep*n/tdu); md_ativ=math.ceil(mativ*n/tdu)

    def rv(m): return round(ritmo*m)
    def st_dot(val,m):
        ok=val>=rv(m); c=VERDE if ok else OLIVA; t="no ritmo" if ok else "atrás"
        return f'<span style="color:{c};font-size:15px;">●</span> <span style="font-size:11px;color:{CINZA}">{t}</span>'
    def hj_chip(val,md):
        ok=val>=md; c=VERDE if ok else RED; sym="✓" if ok else "✗"
        return f'{val} / {md} <span style="color:{c};font-weight:bold;">{sym}</span>'

    # RADAR
    def radar_row(label,val,meta,md):
        return (f'<tr><td style="padding:7px 8px;font-size:13px;color:{NAVY};font-weight:bold;border-bottom:1px solid {LINE};">{label}</td>'
                f'<td style="padding:7px 8px;border-bottom:1px solid {LINE};">{radar_bar(val,meta,rv(meta))}</td>'
                f'<td style="padding:7px 8px;font-size:12px;color:{NAVY};border-bottom:1px solid {LINE};white-space:nowrap;">'
                f'{val} <span style=\'color:{CINZA};font-size:11px\'>/ {meta} ({pct(val,meta)}%)</span></td>'
                f'<td align="center" style="padding:7px 8px;border-bottom:1px solid {LINE};">{st_dot(val,meta)}</td>'
                f'<td align="center" style="padding:7px 8px;font-size:12px;color:{NAVY};border-bottom:1px solid {LINE};white-space:nowrap;">{hj_chip(AD[{"Stage 1":"s1","Stage 3":"s3","Repropostas":"rep","Atividades":"ativ"}.get(label,"s1")],md)}</td></tr>')

    # subst row especial
    sv=pct(AW["sub"],AW["ativ"]); sv_ok=sv>=msub
    subst_row=(f'<tr><td style="padding:7px 8px;font-size:13px;color:{NAVY};font-weight:bold;border-bottom:1px solid {LINE};">Substantivas</td>'
               f'<td style="padding:7px 8px;border-bottom:1px solid {LINE};">{radar_bar(sv,100,msub)}</td>'
               f'<td style="padding:7px 8px;font-size:12px;color:{NAVY};border-bottom:1px solid {LINE};white-space:nowrap;">'
               f'{sv}% <span style=\'color:{CINZA};font-size:11px\'>/ meta {msub}%</span></td>'
               f'<td align="center" style="padding:7px 8px;border-bottom:1px solid {LINE};">'
               f'<span style="color:{VERDE if sv_ok else OLIVA};font-size:15px;">●</span> <span style="font-size:11px;color:{CINZA}">{"no ritmo" if sv_ok else "atrás"}</span></td>'
               f'<td align="center" style="padding:7px 8px;font-size:12px;color:{NAVY};border-bottom:1px solid {LINE};white-space:nowrap;">'
               f'{subd}% <span style="color:{VERDE if subd>=msub else RED};font-weight:bold;">{"✓" if subd>=msub else "✗"}</span></td></tr>')

    radar_rows=radar_row("Stage 1",AW["s1"],TM["s1"],md_s1)+radar_row("Stage 3",AW["s3"],TM["s3"],md_s3)+radar_row("Repropostas",AW["rep"],TM["rep"],md_rep)+radar_row("Atividades",AW["ativ"],TM["ativ"],md_ativ)+subst_row

    # HOJE — chips L-numbers
    def lchips(lst):
        return ", ".join(f'<b style=\'color:{NAVY}\'>{e(L)}</b> <span style=\'color:{CINZA};font-size:11px\'>({e(nm)})</span>' for nm,L in lst) or "—"

    s1h=lchips(data["dia"]["s1"]); s3h=lchips(data["dia"]["s3"]); reph=lchips(data["dia"]["rep"])

    hoje_block=(f'<table role="presentation" width="100%" style="border-collapse:collapse;font-size:13px;">'
                f'<tr><td style="padding:6px 10px;background:{BG3};border:1px solid {LINE};color:{NAVY};width:25%;"><b>Stage 1:</b> {AD["s1"]}</td>'
                f'<td style="padding:6px 10px;background:{BG3};border:1px solid {LINE};color:{NAVY};width:25%;"><b>Stage 3:</b> {AD["s3"]}</td>'
                f'<td style="padding:6px 10px;background:{BG3};border:1px solid {LINE};color:{NAVY};width:25%;"><b>Repropostas:</b> {AD["rep"]}</td>'
                f'<td style="padding:6px 10px;background:{BG3};border:1px solid {LINE};color:{NAVY};"><b>Atividades:</b> {AD["ativ"]} <span style="color:{CINZA};font-size:11px">({AD["sub"]} subst.)</span></td></tr>'
                f'<tr><td colspan="4" style="padding:7px 10px;border:1px solid {LINE};font-size:12px;"><span style="color:{SAGE}">S1:</span> {s1h}</td></tr>'
                f'<tr><td colspan="4" style="padding:7px 10px;border:1px solid {LINE};font-size:12px;"><span style="color:{SAGE}">S3:</span> {s3h}</td></tr>'
                f'<tr><td colspan="4" style="padding:7px 10px;border:1px solid {LINE};font-size:12px;"><span style="color:{SAGE}">Repropostas:</span> {reph}</td></tr>'
                f'</table>')

    # TABELA DIRETORES
    thdr=(f'<thead><tr style="background:{NAVY};color:#fff;">'
          f'<th align="left" style="padding:8px;border:1px solid {NAVY2};">Diretor(a)</th>'
          f'<th align="center" style="padding:8px 6px;border:1px solid {NAVY2};">S1<br><span style="color:{SAGE};font-weight:normal;font-size:10px;">/{ms1}</span></th>'
          f'<th align="center" style="padding:8px 6px;border:1px solid {NAVY2};">S3<br><span style="color:{SAGE};font-weight:normal;font-size:10px;">/{ms3}</span></th>'
          f'<th align="center" style="padding:8px 6px;border:1px solid {NAVY2};">Reprop.<br><span style="color:{SAGE};font-weight:normal;font-size:10px;">/{mrep}</span></th>'
          f'<th align="center" style="padding:8px 6px;border:1px solid {NAVY2};">Atividades<br><span style="color:{SAGE};font-weight:normal;font-size:10px;">semana / dia</span></th>'
          f'<th align="left" style="padding:8px;border:1px solid {NAVY2};">✍️ Substantivas <span style="color:{SAGE};font-weight:normal;font-size:10px;">(meta {msub}%)</span></th></tr></thead>')

    tbody=""
    for i,(nm,v) in enumerate(sorted(data["directors"].items())):
        bg=BG2 if i%2==0 else BG
        sp=pct(v["sub"],v["tot"]); spd=pct(v["subD"],v["totD"])
        tbody+=(f'<tr style="background:{bg};">'
                f'<td style="padding:7px 8px;border:1px solid {LINE};color:{NAVY};">{e(nm)}</td>'
                f'{mini_bar_cell(v["s1"],ms1)}{mini_bar_cell(v["s3"],ms3)}{mini_bar_cell(v["rep"],mrep)}'
                f'<td align="center" style="padding:7px 6px;border:1px solid {LINE};">{v["tot"]} <span style="color:{SAGE}">/</span> {v["totD"]}</td>'
                f'{subst_bar_cell(sp,spd)}</tr>')

    total_row=(f'<tr style="background:{NAVY};color:#fff;font-weight:bold;">'
               f'<td style="padding:7px 8px;border:1px solid {NAVY2};">TIME ({n})</td>'
               f'<td align="center" style="padding:7px 6px;border:1px solid {NAVY2};">{AW["s1"]}</td>'
               f'<td align="center" style="padding:7px 6px;border:1px solid {NAVY2};">{AW["s3"]}</td>'
               f'<td align="center" style="padding:7px 6px;border:1px solid {NAVY2};">{AW["rep"]}</td>'
               f'<td align="center" style="padding:7px 6px;border:1px solid {NAVY2};">{AW["ativ"]} / {AD["ativ"]}</td>'
               f'<td style="padding:7px 8px;border:1px solid {NAVY2};">{subw}% | dia {subd}% · meta {msub}%</td></tr>')

    # MOVIMENTAÇÕES
    mov_rows=""
    for nm in sorted(data["mov"].keys()):
        mov=data["mov"][nm]; parts=[]
        for k,label in [("s1","S1"),("s3","S3"),("rep","Reprop")]:
            lst=mov.get(k,[])
            if lst:
                items=" ".join(f'<b style="color:{AZUL};">{e(L)}</b>' if t else e(L) for L,t in lst)
                parts.append(f'{label}: {items}')
        if parts:
            mov_rows+=(f'<tr><td style="padding:4px 8px;font-size:12px;font-weight:bold;color:{NAVY};width:160px;">{e(nm)}</td>'
                       f'<td style="padding:4px 8px;font-size:11.5px;color:{NAVY};">{" · ".join(parts)}</td></tr>')

    # DESTAQUES
    dest_d=data.get("destaque_dia",""); dest_s=data.get("destaque_semana","")
    def dest_box(label, txt):
        return (f'<table role="presentation" width="100%"><tr>'
                f'<td style="background:{BG3};border-left:4px solid {AZUL};padding:9px 14px;font-size:13px;color:{NAVY};">'
                f'<b>{e(label)}</b> <span style="color:{CINZA}">{e(txt)}</span></td></tr></table>')

    rodape=(f'Metas/diretor: S1 {ms1} · S3 {ms3} · Repropostas {mrep} · Atividades {mativ} (20/dia) · '
            f'Substantivas {msub}% (7 de 20/dia). '
            f'Dia = campo do estágio com data = {dt.day:02d}/{dt.month:02d} (S1: lease economics · S3: stage3date · Reprop: createdon). '
            f'Reproposta v2 = pricing do dono atual em deal herdado (S3/S5 movidos por outro), '
            f'ou 2ª+ pricing quando ele mesmo moveu o estágio; 1x por opp/semana. '
            f'Atividade substantiva = descrição estratégica (≥180 car. ou ≥140 com 2+ sinais). '
            f'Dados via Web API Dynamics 365. Uso interno.')

    sem_label=semjan.replace("–","–").replace("-","–") if semjan else ""

    HTML=(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
          f'style="background:#eef2f6;margin:0;padding:24px 0;"><tr><td align="center">\n'
          f'<table role="presentation" width="900" cellpadding="0" cellspacing="0" '
          f'style="width:900px;max-width:900px;background:{BG};border:1px solid #d6dee6;font-family:Arial,Helvetica,sans-serif;">\n'
          # HEADER
          f'<tr><td style="background:{NAVY};padding:18px 26px;"><table role="presentation" width="100%"><tr>'
          f'<td align="left" valign="middle"><span style="font-size:26px;font-weight:bold;color:#fff;letter-spacing:1px;">APW</span>'
          f'<span style="font-size:26px;color:{SAGE};letter-spacing:2px;">Brasil</span></td>'
          f'<td align="right" valign="middle" style="color:#fff;font-size:13px;">'
          f'<span style="font-size:15px;font-weight:bold;">Reporte Diário — Movimentações CRM Brasil</span><br>'
          f'<span style="color:{SAGE};font-size:12px;">Diretoria de Aquisições</span></td></tr></table></td></tr>\n'
          f'<tr><td style="background:{AZUL};height:4px;font-size:0;line-height:4px;">&nbsp;</td></tr>\n'
          # DATA
          f'<tr><td style="padding:16px 26px 4px;">'
          f'<span style="font-size:18px;font-weight:bold;color:{NAVY};">{e(data_fmt)}</span>'
          f'<span style="font-size:13px;color:{CINZA};">&nbsp;·&nbsp; Semana {e(sem_label)} &nbsp;·&nbsp; dia '
          f'<b style="color:{AZUL};">{dec} de {tdu}</b> (ritmo esperado {round(ritmo*100)}%)</span></td></tr>\n'
          # RADAR
          f'<tr><td style="padding:12px 26px 4px;"><div style="font-size:14px;font-weight:bold;color:{NAVY};border-bottom:2px solid {AZUL};padding-bottom:4px;">📡 RADAR DA EQUIPE</div></td></tr>\n'
          f'<tr><td style="padding:8px 26px 14px;"><table role="presentation" width="100%" style="border-collapse:collapse;background:{BG4};border:1px solid {LINE};">\n'
          f'<tr style="background:{HBDR};"><th align="left" style="padding:7px 8px;font-size:11px;color:{NAVY};">Métrica</th>'
          f'<th align="left" style="padding:7px 8px;font-size:11px;color:{NAVY};">Progresso da semana '
          f'<span style="font-weight:normal;color:{CINZA}">(| = ritmo {round(ritmo*100)}%)</span></th>'
          f'<th align="left" style="padding:7px 8px;font-size:11px;color:{NAVY};">Semana</th>'
          f'<th align="center" style="padding:7px 8px;font-size:11px;color:{NAVY};">Status</th>'
          f'<th align="center" style="padding:7px 8px;font-size:11px;color:{NAVY};">Hoje (real / meta)</th></tr>\n'
          f'{radar_rows}</table></td></tr>\n'
          # HOJE
          f'<tr><td style="padding:8px 26px 4px;"><div style="font-size:14px;font-weight:bold;color:{NAVY};border-bottom:2px solid {AZUL};padding-bottom:4px;">📌 HOJE — {dt.day:02d}/{dt.month:02d}</div></td></tr>\n'
          f'<tr><td style="padding:8px 26px;">{hoje_block}</td></tr>\n'
          # DESTAQUE DIA
          f'<tr><td style="padding:4px 26px 12px;">{dest_box("Destaque do dia.", dest_d)}</td></tr>\n'
          # TABELA SEMANA
          f'<tr><td style="padding:8px 26px 4px;"><div style="font-size:14px;font-weight:bold;color:{NAVY};border-bottom:2px solid {AZUL};padding-bottom:4px;">📊 ACUMULADO DA SEMANA ({e(sem_label)})</div></td></tr>\n'
          f'<tr><td style="padding:4px 26px 0;"><table role="presentation" width="100%" style="border-collapse:collapse;font-size:12px;">'
          f'{thdr}<tbody>{tbody}{total_row}</tbody></table></td></tr>\n'
          # DESTAQUE SEMANA
          f'<tr><td style="padding:8px 26px 12px;">{dest_box("Destaque da semana.", dest_s)}</td></tr>\n'
          # MOVIMENTAÇÕES
          f'<tr><td style="padding:8px 26px 4px;"><div style="font-size:14px;font-weight:bold;color:{NAVY};border-bottom:2px solid {AZUL};padding-bottom:4px;">🔁 MOVIMENTAÇÕES DA SEMANA — L-numbers</div>\n'
          f'<div style="font-size:11px;color:{CINZA};margin-top:4px;">Em <b style="color:{AZUL};">azul</b> = movido hoje ({dt.day:02d}/{dt.month:02d}).</div></td></tr>\n'
          f'<tr><td style="padding:4px 26px 16px;"><table role="presentation" width="100%">{mov_rows}</table></td></tr>\n'
          # RODAPÉ
          f'<tr><td style="background:{NAVY};padding:14px 26px;">'
          f'<div style="font-size:12px;color:{SAGE};">{RAZAO}</div>'
          f'<div style="font-size:10.5px;color:#6a8099;margin-top:5px;">{e(rodape)}</div>'
          f'</td></tr>\n'
          f'</table></td></tr></table>')

    stem=f"reporte-crm-apw-{alvo}"
    html_path=out_dir/f"{stem}.html"
    html_path.write_text(HTML,encoding="utf-8")

    png_path=out_dir/f"{stem}.png"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br=p.chromium.launch()
            pg=br.new_page(viewport={"width":960,"height":800})
            pg.set_content(HTML,wait_until="networkidle")
            el=pg.query_selector("table[width='900']")
            el.screenshot(path=str(png_path))
            br.close()
        print(f"OK html+png: {html_path} {png_path}")
    except Exception as ex:
        print(f"HTML ok, render falhou: {ex}")

if __name__=="__main__":
    main()
