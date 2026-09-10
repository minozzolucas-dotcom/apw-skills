#!/usr/bin/env python3
"""
APW Diretor Pace Score — v2
Contagem pura de moves por stage (S1, S3, S8, S99), sem score composto.
"""
import json
import sys
from datetime import datetime, date
from collections import defaultdict
from pathlib import Path

# CLI: --today=YYYY-MM-DD, --harvest=path, --out=path
def _arg(name, default):
    prefix = f'--{name}='
    for a in sys.argv[1:]:
        if a.startswith(prefix):
            return a[len(prefix):]
    return default

HARVEST_PATH = _arg('harvest', 'harvest.json')
OUT_HTML = _arg('out', 'apw_pace_dashboard.html')
_today_arg = _arg('today', None)
TODAY = datetime.strptime(_today_arg, '%Y-%m-%d').date() if _today_arg else date.today()

# Stages de interesse (Lucas 09/09: sem S5)
STAGES = [
    ('s1',  'Stage 1',  'Qualificação'),
    ('s3',  'Stage 3',  'Pricing Option'),
    ('s8',  'Stage 8',  'Submission'),
    ('s99', 'Stage 99', 'Closed & Funded'),
]

DIRECTOR_TITLES = {
    'Acquisition Director', 'Sr Acquisition Director',
    'Director, Commercial Sale', 'Director, Sales',
}
EXCLUDE_NAMES = {'Lucas Minozzo'}
ONBOARDING_DAYS = 90

# ============ LOAD ============
d = json.load(open(HARVEST_PATH))
directors = {}
for oid, o in d['owners'].items():
    if o.get('title') in DIRECTOR_TITLES and not o.get('isdisabled', True):
        if o['fullname'] in EXCLUDE_NAMES:
            continue
        # Prefere new_adphiredate (data real do ADP); fallback pra createdon
        adp = o.get('new_adphiredate')
        source = 'adp'
        if adp:
            hire = datetime.fromisoformat(adp.replace('Z','+00:00')).date()
        else:
            hire = datetime.fromisoformat(o['createdon'].replace('Z','+00:00')).date()
            source = 'createdon (proxy)'
        directors[oid] = {'id': oid, 'name': o['fullname'], 'title': o['title'],
                          'hire_date': hire, 'hire_source': source}

# stage_activity[oid][stage_key][(y,m)] = count
stage_activity = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for stage_key, rows in d['stages'].items():
    if not isinstance(rows, list): continue
    for r in rows:
        oid = r['ownerId']
        if oid not in directors: continue
        stage_activity[oid][stage_key][(r['year'], r['month'])] += r['count']

# ============ HELPERS ============
def window_months(reference_date, n_months):
    """Últimos N meses COMPLETOS antes da reference_date."""
    yr, mo = reference_date.year, reference_date.month
    months = []
    for i in range(1, n_months + 1):
        m = mo - i
        y = yr
        while m <= 0:
            m += 12; y -= 1
        months.append((y, m))
    return set(months)

def all_months_since(hire_date, until_date):
    """Todos os (y,m) desde hire até o último mês COMPLETO antes de until."""
    months = []
    y, m = hire_date.year, hire_date.month
    end_y, end_m = until_date.year, until_date.month - 1
    if end_m == 0: end_m = 12; end_y -= 1
    while (y, m) <= (end_y, end_m):
        months.append((y, m))
        m += 1
        if m > 12: m = 1; y += 1
    return set(months)

def count_in(oid, stage_key, month_set):
    counts = stage_activity[oid].get(stage_key, {})
    return sum(c for (y,m), c in counts.items() if (y,m) in month_set)

# ============ WINDOWS ============
w_1m = window_months(TODAY, 1)
w_3m = window_months(TODAY, 3)
w_6m = window_months(TODAY, 6)
w_12m = window_months(TODAY, 12)
month_curr = {(TODAY.year, TODAY.month)}

# ============ CALC ============
results = []
for oid, meta in directors.items():
    hire = meta['hire_date']
    days_since = (TODAY - hire).days
    is_onboarding = days_since < ONBOARDING_DAYS
    baseline_months = all_months_since(hire, TODAY)
    n_base = max(len(baseline_months), 1)
    
    r = {
        'id': oid, 'name': meta['name'], 'title': meta['title'],
        'hire_date': hire.isoformat(), 'days_since_hire': days_since,
        'is_onboarding': is_onboarding, 'baseline_months': n_base,
        'stages': {},
    }
    
    for skey, slbl, sdesc in STAGES:
        base_total = count_in(oid, skey, baseline_months)
        base_monthly = base_total / n_base
        
        def calc(window_set):
            active = window_set & baseline_months
            total = count_in(oid, skey, window_set)
            monthly = total / max(len(active), 1) if active else 0
            pi = monthly / base_monthly if base_monthly > 0 else None
            return {'total': total, 'monthly': monthly, 'pi': pi, 'n_months': len(active)}
        
        curr_total = count_in(oid, skey, month_curr)
        projected = curr_total * (30 / TODAY.day) if TODAY.day > 0 else 0
        
        r['stages'][skey] = {
            'label': slbl, 'desc': sdesc,
            'baseline_total': base_total, 'baseline_monthly': base_monthly,
            'w_12m': calc(w_12m),
            'w_6m': calc(w_6m),
            'w_3m': calc(w_3m),
            'w_1m': calc(w_1m),
            'curr': curr_total,
            'curr_projected': projected,
        }
    
    # PI médio 3m (só stages com baseline > 0)
    pis_3m = [r['stages'][s]['w_3m']['pi'] for s,_,_ in STAGES if r['stages'][s]['w_3m']['pi'] is not None]
    r['pi_3m_avg'] = sum(pis_3m)/len(pis_3m) if pis_3m else None
    
    # PI 3m de S99 (fechamento) — critério de ranking secundário
    r['pi_3m_s99'] = r['stages']['s99']['w_3m']['pi']
    
    results.append(r)

# Ordena por PI 3m médio
def sort_key(r):
    if r['is_onboarding']: return (1, 0)
    pi = r['pi_3m_avg']
    return (0, -pi if pi is not None else 0)
results.sort(key=sort_key)

# ============ CLASSIFY ============
def pi_class(pi):
    if pi is None: return ('sem_dado', '—', '#5D5D5D')
    if pi >= 1.3: return ('acelerando_forte', '🔥 Acelerando forte', '#009877')
    if pi >= 1.0: return ('acima', '🟢 Acima', '#5FBF8B')
    if pi >= 0.8: return ('leve_queda', '🟡 Leve queda', '#A7AF00')
    if pi >= 0.5: return ('desacelerando', '🟠 Desacelerando', '#D97706')
    return ('queda_livre', '🔴 Queda livre', '#B91C1C')

def trend(r):
    pi3 = r['pi_3m_avg']
    pi12 = [r['stages'][s]['w_12m']['pi'] for s,_,_ in STAGES if r['stages'][s]['w_12m']['pi'] is not None]
    if pi3 is None or not pi12: return ('—', '#5D5D5D', 'sem base')
    pi12_avg = sum(pi12)/len(pi12)
    delta = pi3 - pi12_avg
    if delta > 0.2: return ('▲▲', '#009877', 'acelerando vs. tendência longa')
    if delta > 0.05: return ('▲', '#5FBF8B', 'ligeira aceleração')
    if delta > -0.05: return ('=', '#91A5A4', 'estável')
    if delta > -0.2: return ('▼', '#A7AF00', 'ligeira desaceleração')
    return ('▼▼', '#B91C1C', 'desaceleração forte')

# ============ HTML ============
def fmt_num(n, decimals=1):
    if isinstance(n, int) or (isinstance(n, float) and n == int(n)):
        return str(int(n))
    return f"{n:.{decimals}f}"

def cell_html(count, pi, subtitle=None):
    """Renderiza uma célula: número grande + PI pequeno colorido."""
    if pi is None:
        pi_html = '<span class="pi-tag pi-none">—</span>'
    else:
        _, _, color = pi_class(pi)
        pi_html = f'<span class="pi-tag" style="background:{color}">PI {pi:.2f}</span>'
    sub = f'<div class="cell-sub">{subtitle}</div>' if subtitle else ''
    return f'<div class="cell-count">{fmt_num(count)}</div>{pi_html}{sub}'

html_parts = [f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>APW · Pace Score · Brasil</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, Helvetica, sans-serif; background: #0a1224; color: #dbe4ee; padding: 28px; line-height: 1.4; }}
  .brand-header {{ display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3px solid #1C75BB; padding-bottom: 18px; margin-bottom: 24px; }}
  .brand-wordmark {{ font-size: 26px; font-weight: bold; }}
  .brand-wordmark .apw {{ color: #fff; }}
  .brand-wordmark .brasil {{ color: #91A5A4; }}
  .brand-sub {{ color: #91A5A4; font-size: 13px; margin-top: 4px; }}
  .meta {{ text-align: right; color: #91A5A4; font-size: 12px; }}
  .meta strong {{ color: #dbe4ee; }}
  h1 {{ color: #fff; font-size: 20px; margin-bottom: 6px; font-weight: normal; }}
  .subtitle {{ color: #91A5A4; font-size: 13px; margin-bottom: 20px; }}
  .legend {{ display: flex; gap: 14px; flex-wrap: wrap; background: #151f2c; padding: 10px 14px;
    border-radius: 5px; margin-bottom: 22px; font-size: 11px; color: #91A5A4; }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  .legend-dot {{ width: 9px; height: 9px; border-radius: 50%; }}
  .director-card {{ background: #151f2c; border-left: 4px solid var(--card-color, #1C75BB);
    border-radius: 5px; padding: 16px 20px; margin-bottom: 14px; }}
  .card-header {{ display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }}
  .director-name {{ font-size: 17px; font-weight: bold; color: #fff; }}
  .director-title {{ color: #91A5A4; font-size: 11px; margin-left: 8px; }}
  .director-tenure {{ color: #91A5A4; font-size: 11px; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold; margin-left: 10px; }}
  .badge-onboarding {{ background: #012B5E; color: #91A5A4; }}
  .trend {{ font-size: 16px; margin-left: 6px; }}
  
  table.stage-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }}
  table.stage-table th {{ background: #0a1224; color: #91A5A4; text-transform: uppercase;
    font-size: 10px; font-weight: normal; padding: 8px 6px; letter-spacing: 0.4px; text-align: center;
    border-bottom: 1px solid #1a2438; }}
  table.stage-table th.stage-col {{ text-align: left; padding-left: 12px; }}
  table.stage-table td {{ padding: 10px 6px; text-align: center; border-bottom: 1px solid #1a2438; vertical-align: top; }}
  table.stage-table td.stage-col {{ text-align: left; padding-left: 12px; }}
  table.stage-table tr:last-child td {{ border-bottom: none; }}
  
  .stage-label {{ color: #fff; font-weight: bold; font-size: 13px; }}
  .stage-desc {{ color: #91A5A4; font-size: 10px; margin-top: 1px; }}
  
  .cell-count {{ color: #fff; font-size: 16px; font-weight: bold; line-height: 1.1; }}
  .cell-sub {{ color: #91A5A4; font-size: 10px; margin-top: 2px; }}
  .pi-tag {{ display: inline-block; margin-top: 4px; padding: 1px 6px; border-radius: 2px;
    font-size: 10px; font-weight: bold; color: #fff; }}
  .pi-none {{ background: #5D5D5D; color: #dbe4ee; }}
  
  .baseline-cell {{ background: rgba(145, 165, 164, 0.08); }}
  .curr-cell {{ background: rgba(28, 117, 187, 0.10); }}
  
  .footer {{ margin-top: 32px; padding-top: 18px; border-top: 1px solid #1a2438;
    color: #5D5D5D; font-size: 10px; text-align: center; }}
  .footer strong {{ color: #91A5A4; }}
</style></head><body>

<div class="brand-header">
  <div>
    <div class="brand-wordmark"><span class="apw">APW</span><span class="brasil">Brasil</span></div>
    <div class="brand-sub">Diretor Pace Score · Time de Aquisições</div>
  </div>
  <div class="meta">
    <div>Referência: <strong>{TODAY.strftime('%d/%m/%Y')}</strong></div>
    <div>Fonte: Dynamics 365 · FetchXML aggregate</div>
    <div>Ranking: <strong>{sum(1 for r in results if not r['is_onboarding'])}</strong> ativos + {sum(1 for r in results if r['is_onboarding'])} em onboarding</div>
  </div>
</div>

<h1>Pace Score — contagem de moves por stage vs. média histórica</h1>
<div class="subtitle">
  Pace Index (PI) = moves/mês na janela recente ÷ baseline mensal do próprio diretor.
  PI &gt; 1 = mais rápido que a própria média; PI &lt; 1 = mais lento. Ranking ordenado pelo PI 3m médio dos 4 stages.
</div>

<div class="legend">
  <div class="legend-item"><span class="legend-dot" style="background:#009877"></span>PI ≥ 1.3 · Acelerando forte</div>
  <div class="legend-item"><span class="legend-dot" style="background:#5FBF8B"></span>PI 1.0–1.3 · Acima da média</div>
  <div class="legend-item"><span class="legend-dot" style="background:#A7AF00"></span>PI 0.8–1.0 · Leve queda</div>
  <div class="legend-item"><span class="legend-dot" style="background:#D97706"></span>PI 0.5–0.8 · Desacelerando</div>
  <div class="legend-item"><span class="legend-dot" style="background:#B91C1C"></span>PI &lt; 0.5 · Queda livre</div>
</div>
''']

for r in results:
    pi_avg = r['pi_3m_avg']
    _, cls_lbl, cls_color = pi_class(pi_avg)
    arrow_txt, arrow_color, arrow_desc = trend(r)
    hire_fmt = datetime.fromisoformat(r['hire_date']).strftime('%d/%m/%Y')
    tenure = r['baseline_months']
    tenure_txt = f"{tenure}m de casa" if tenure < 24 else f"{tenure//12}a{tenure%12:02d}m de casa"
    ob_badge = f'<span class="badge badge-onboarding">ONBOARDING · {r["days_since_hire"]}d</span>' if r['is_onboarding'] else ''
    
    # Constrói linhas da tabela (uma por stage)
    rows_html = []
    for skey, slbl, sdesc in STAGES:
        s = r['stages'][skey]
        base_sub = f"{s['baseline_total']} em {tenure}m"
        rows_html.append(f'''<tr>
            <td class="stage-col">
                <div class="stage-label">{slbl}</div>
                <div class="stage-desc">{sdesc}</div>
            </td>
            <td class="baseline-cell">
                <div class="cell-count">{s['baseline_monthly']:.1f}</div>
                <div class="cell-sub">/mês · {base_sub}</div>
            </td>
            <td>{cell_html(s['w_12m']['monthly'], s['w_12m']['pi'], subtitle=f"{s['w_12m']['total']} em 12m")}</td>
            <td>{cell_html(s['w_6m']['monthly'], s['w_6m']['pi'], subtitle=f"{s['w_6m']['total']} em 6m")}</td>
            <td>{cell_html(s['w_3m']['monthly'], s['w_3m']['pi'], subtitle=f"{s['w_3m']['total']} em 3m")}</td>
            <td>{cell_html(s['w_1m']['total'], s['w_1m']['pi'], subtitle="ago/26")}</td>
            <td class="curr-cell">
                <div class="cell-count">{s['curr']}</div>
                <div class="cell-sub">proj: {s['curr_projected']:.1f}</div>
            </td>
        </tr>''')
    
    pi_avg_html = f'PI médio 3m: <strong>{pi_avg:.2f}</strong>' if pi_avg else 'PI médio 3m: —'
    
    html_parts.append(f'''
<div class="director-card" style="--card-color:{cls_color}">
    <div class="card-header">
        <div>
            <span class="director-name">{r['name']}</span>
            <span class="director-title">· {r['title']}</span>
            {ob_badge}
        </div>
        <div>
            <span style="color:{cls_color};font-weight:bold;font-size:13px">{cls_lbl}</span>
            <span class="trend" style="color:{arrow_color}" title="{arrow_desc}">{arrow_txt}</span>
            <span class="director-tenure" style="margin-left:12px">Hire: {hire_fmt} · {tenure_txt} · {pi_avg_html}</span>
        </div>
    </div>
    <table class="stage-table">
        <thead>
            <tr>
                <th class="stage-col">Stage</th>
                <th>Baseline<br><span style="font-size:9px">média histórica</span></th>
                <th>Últ. 12m</th>
                <th>Últ. 6m</th>
                <th>Últ. 3m</th>
                <th>Último mês<br><span style="font-size:9px">ago/26</span></th>
                <th>Mês em curso<br><span style="font-size:9px">set/26 (dia {TODAY.day})</span></th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows_html)}
        </tbody>
    </table>
</div>
''')

html_parts.append(f'''
<div class="footer">
  <strong>Metodologia</strong> · Contagem pura de moves de stage por diretor · Baseline = total desde hire date ÷ meses ativos ·
  PI = ritmo mensal recente ÷ baseline · Diretores com &lt;{ONBOARDING_DAYS}d de casa entram em ONBOARDING (não pontuam pace) ·
  Trend = PI 3m vs PI 12m · Hire date = createdon do systemuser (proxy, trocar por new_adphiredate) ·
  Gerado em {TODAY.strftime('%d/%m/%Y')} · <strong>APWireless Brasil Invest. Imob. LTDA</strong>
</div>

</body></html>
''')

Path(OUT_HTML).write_text(''.join(html_parts), encoding='utf-8')
print(f"✅ Dashboard v2 salvo em {OUT_HTML}")

# Ranking condensado
print("\n=== RANKING v2 (por PI 3m médio das 4 stages) ===")
print(f"{'Nome':<24s} {'PI 3m avg':>10s} {'S1 PI':>7s} {'S3 PI':>7s} {'S8 PI':>7s} {'S99 PI':>7s}")
for r in results:
    pi_avg = f"{r['pi_3m_avg']:.2f}" if r['pi_3m_avg'] else " -- "
    def pf(s):
        pi = r['stages'][s]['w_3m']['pi']
        return f"{pi:.2f}" if pi is not None else " -- "
    ob = " [ONB]" if r['is_onboarding'] else ""
    print(f"  {r['name']:<24s} {pi_avg:>10s} {pf('s1'):>7s} {pf('s3'):>7s} {pf('s8'):>7s} {pf('s99'):>7s}{ob}")
