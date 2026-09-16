#!/usr/bin/env python3
"""
Parse APW Brasil ISW (Investment Worksheet) — supports both .xlsx and .xlsb.

Usage:
    python3 parse_isw.py <path_to_isw.xlsx_or_xlsb>

Output: JSON to stdout — projected costs + deal narrative + carrier info
"""

import sys, json, re

ITEM_KEYWORDS = {
    "title_work":       ["title search", "title work", "certidão", "certidoes", "documentos", "correio"],
    "notary":           ["notary", "cartório", "cartorio", "tabelião", "escritura"],
    "recording":        ["recording", "registro", "custo de registro"],
    "legal_fees":       ["legal fees", "legal fee", "outside legal", "honorário", "honorario", "third party"],
    "site_owner_legal": ["site owner", "advogado", "auxílio adv", "auxilio adv"],
    "site_inspection":  ["site inspection", "inspeção", "inspecao", "vistoria"],
    "broker":           ["broker", "agent fee", "intermediary", "corretor"],
    "installments":     ["installment", "parcela"],
    "rent_proration":   ["proration", "prorrateio", "pro-rata", "pro rata"],
}

def to_float(value):
    if value is None: return None
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace('R$','').replace(' ','').replace('.','').replace(',','.')
        try: return float(cleaned)
        except ValueError: return None
    return None

def match_key(text, keywords):
    t = text.lower()
    return any(kw in t for kw in keywords)

def parse_rows(rows_iter):
    """Generic row parser — works on any iterable of (col_index → value) dicts."""
    projected = {}
    deal_info = {}

    for row_idx, row in enumerate(rows_iter):
        # row is a list of values indexed by column position
        if not any(v is not None for v in row):
            continue

        # Try to find the label (first non-empty string cell)
        label = None
        for cell in row:
            if cell and isinstance(cell, str) and len(cell.strip()) > 3:
                label = cell.strip()
                break

        if not label:
            continue

        # Extract deal metadata from Submission Sheet structure
        label_lower = label.lower()
        if 'transaction name' in label_lower and len(row) > 4 and row[4]:
            deal_info['transaction_name'] = str(row[4]).strip()
        elif 'crm number' in label_lower and len(row) > 4 and row[4]:
            deal_info['l_number'] = str(row[4]).strip()
        elif 'asset type' in label_lower and len(row) > 4 and row[4]:
            deal_info['asset_type'] = str(row[4]).strip()
            if len(row) > 6 and row[6]:
                deal_info['sub_asset_type'] = str(row[6]).strip()
        elif 'transaction type' in label_lower and len(row) > 4 and row[4]:
            deal_info['transaction_type'] = str(row[4]).strip()
        elif 'transaction term' in label_lower and len(row) > 4:
            v = to_float(row[4])
            if v: deal_info['term_years'] = int(v)
        elif 'site city' in label_lower and len(row) > 4 and row[4]:
            city = str(row[4]).strip()
            state = str(row[5]).strip() if len(row) > 5 and row[5] else ''
            deal_info['location'] = f"{city}, {state}".strip(', ')
        elif 'landlord name' in label_lower and len(row) > 4 and row[4]:
            deal_info['landlord'] = str(row[4]).strip()
        elif 'key notes' in label_lower or (row_idx == 11 and len(row) > 9 and row[9] and
             isinstance(row[9], str) and 'investment opportunity' in row[9].lower()):
            # Key Notes is in col J (index 9) of row 12 (idx 11)
            for i, cell in enumerate(row):
                if cell and isinstance(cell, str) and 'investment opportunity' in cell.lower():
                    deal_info['key_notes'] = cell.strip()
                    break

        # Match cost line items
        for key, keywords in ITEM_KEYWORDS.items():
            if key in projected:
                continue
            if match_key(label, keywords):
                for cell in row:
                    v = to_float(cell)
                    if v and abs(v) > 10:  # ignore tiny rounding values
                        projected[key] = abs(v)
                        break
                break

    return {'projected_costs': projected, 'deal_info': deal_info}


def parse_isw(filepath):
    ext = filepath.lower().split('.')[-1]

    if ext == 'xlsb':
        try:
            import pyxlsb
        except ImportError:
            import subprocess
            subprocess.run(['pip', 'install', 'pyxlsb', '--break-system-packages', '-q'], check=True)
            import pyxlsb

        results = {}
        with pyxlsb.open_workbook(filepath) as wb:
            # Try Submission Sheet first, then first sheet
            target_sheets = ['Submission Sheet', wb.sheets[0]] if wb.sheets else []
            for sname in wb.sheets:
                if 'submission' in sname.lower():
                    target_sheets = [sname]
                    break

            for sname in target_sheets[:1]:
                with wb.get_sheet(sname) as ws:
                    rows = []
                    for row in ws.rows():
                        rows.append([c.v for c in row])
                    results = parse_rows(rows)

        return results

    else:  # .xlsx
        import openpyxl
        wb = openpyxl.load_workbook(filepath, data_only=True)

        target = None
        for name in wb.sheetnames:
            if 'submission' in name.lower():
                target = wb[name]
                break
        if not target:
            target = wb.worksheets[0]

        rows = [list(r) for r in target.iter_rows(values_only=True)]
        return parse_rows(rows)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_isw.py <path>", file=sys.stderr)
        sys.exit(1)
    data = parse_isw(sys.argv[1])
    print(json.dumps(data, indent=2, ensure_ascii=False))
