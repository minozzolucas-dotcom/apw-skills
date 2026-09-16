#!/usr/bin/env python3
"""
parse_activities.py — Parser robusto de view de atividades do Dynamics 365 (APW Brasil).

Lê o texto colado de uma view de atividades de uma oportunidade (ou várias) e
devolve JSON estruturado, ordenado cronologicamente, agrupado por código L.

Lida com:
- Descrições multi-linha (bullets, mensagens de WhatsApp coladas, parágrafos)
- Activity Owner vazio ou 'undefined' (tasks automáticas da calculadora)
- Actual End vazio (atividades Open)
- Ordem invertida na view (reordena por Created On ascendente)
- Múltiplas opps no mesmo input (agrupa por código L)

Uso:
    python3 parse_activities.py <arquivo_input.txt>
    python3 parse_activities.py <arquivo_input.txt> --out resultado.json

Se nenhum --out for dado, imprime o JSON no stdout.
"""

import sys
import re
import json
import argparse

# Tipos de atividade que marcam o início de um novo registro.
# Ajuste se a APW usar outros tipos (phonecall, appointment, email...).
ACTIVITY_TYPES = ("task", "phonecall", "appointment", "email", "letter", "fax")

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$")
L_CODE = re.compile(r"\bL\d{6,8}\b")


def is_record_start(line):
    """Uma linha inicia um registro se começa com um tipo de atividade seguido de TAB."""
    stripped = line.lstrip()
    for t in ACTIVITY_TYPES:
        if stripped.lower().startswith(t + "\t") or stripped.lower() == t:
            return True
    return False


def split_records(raw):
    """Divide o texto bruto em blocos de registro, respeitando descrições multi-linha."""
    lines = raw.splitlines()
    records = []
    current = []
    for line in lines:
        # Pula o cabeçalho da view e a linha de títulos de coluna.
        low = line.strip().lower()
        if low.startswith("subject\t") or "activities found" in low:
            continue
        if is_record_start(line):
            if current:
                records.append("\n".join(current))
            current = [line]
        else:
            if current:  # linha de continuação da descrição
                current.append(line)
            # se current vazio e a linha não é início de registro, é lixo de cabeçalho -> ignora
    if current:
        records.append("\n".join(current))
    return records


def parse_record(block):
    """Parseia um bloco de registro em um dict estruturado.

    Estratégia: o bloco pode ter quebras de linha internas (na descrição).
    Junta tudo, depois divide por TAB. A estrutura esperada é:
      tipo TAB subject TAB description TAB owner TAB status TAB created_on TAB actual_end
    A descrição pode conter TABs? Raramente. Mas pode conter \n — por isso
    juntamos o bloco com \n preservado dentro do campo description.
    """
    # Junta as linhas do bloco preservando \n; depois separa por TAB.
    # O truque: o primeiro \n-join recompõe a descrição; os campos reais
    # são delimitados por TAB.
    joined = block.replace("\r", "")
    parts = joined.split("\t")
    parts = [p.strip("\n") for p in parts]

    rec = {
        "activity_type": parts[0].strip() if len(parts) > 0 else "",
        "subject": parts[1].strip() if len(parts) > 1 else "",
        "description": parts[2] if len(parts) > 2 else "",
        "owner": parts[3].strip() if len(parts) > 3 else "",
        "status": parts[4].strip() if len(parts) > 4 else "",
        "created_on": parts[5].strip() if len(parts) > 5 else "",
        "actual_end": parts[6].strip() if len(parts) > 6 else "",
    }

    # Normaliza owner vazio/undefined
    if not rec["owner"] or rec["owner"].lower() == "undefined":
        rec["owner"] = "Sistema (Calculator)"

    # Extrai código L da descrição ou do subject
    text_for_l = rec["subject"] + " " + rec["description"]
    m = L_CODE.search(text_for_l)
    rec["l_code"] = m.group(0) if m else None

    return rec


def sort_key(rec):
    co = rec.get("created_on", "")
    return co if ISO_DATE.match(co) else "0000-00-00T00:00:00Z"


def main():
    ap = argparse.ArgumentParser(description="Parser de view de atividades do Dynamics 365.")
    ap.add_argument("input", help="Arquivo de texto com a view de atividades colada.")
    ap.add_argument("--out", help="Arquivo JSON de saída (default: stdout).")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    blocks = split_records(raw)
    records = [parse_record(b) for b in blocks if b.strip()]

    # Ordena cronologicamente (mais antigo primeiro)
    records.sort(key=sort_key)

    # Agrupa por código L. Atividades sem L herdam o L dominante do input.
    all_l = [r["l_code"] for r in records if r["l_code"]]
    dominant_l = max(set(all_l), key=all_l.count) if all_l else None

    groups = {}
    for r in records:
        key = r["l_code"] or dominant_l or "UNKNOWN"
        groups.setdefault(key, []).append(r)

    result = {
        "opps": [
            {
                "l_code": l,
                "activity_count": len(acts),
                "date_range": {
                    "first": acts[0]["created_on"] if acts else None,
                    "last": acts[-1]["created_on"] if acts else None,
                },
                "owners": sorted(set(a["owner"] for a in acts)),
                "activities": acts,
            }
            for l, acts in groups.items()
        ],
        "total_activities": len(records),
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"OK: {len(records)} atividades, {len(groups)} opp(s) -> {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
