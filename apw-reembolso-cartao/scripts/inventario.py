#!/usr/bin/env python3
"""Inventaria os anexos do reembolso: tipo, tamanho, MD5 e duplicatas exatas.

Uso: python3 inventario.py /mnt/user-data/uploads
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

EXT_IMAGEM = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".webp"}
EXT_PDF = {".pdf"}
EXT_PLANILHA = {".xlsx", ".xls", ".csv"}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def classifica(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in EXT_PLANILHA:
        return "PLANILHA (candidato a Form C/C)"
    if ext in EXT_PDF:
        return "PDF"
    if ext in EXT_IMAGEM:
        return "IMAGEM (candidato a NF)"
    return "OUTRO"


def main() -> int:
    pasta = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads")
    arquivos = sorted(p for p in pasta.rglob("*") if p.is_file())
    if not arquivos:
        print(f"Nenhum arquivo em {pasta}")
        return 1

    por_hash = defaultdict(list)
    print(f"{'ARQUIVO':<45} {'TIPO':<32} {'KB':>8}  MD5")
    print("-" * 110)
    for p in arquivos:
        h = md5(p)
        por_hash[h].append(p)
        print(f"{p.name[:44]:<45} {classifica(p):<32} {p.stat().st_size/1024:>8.0f}  {h[:12]}")

    dups = {h: ps for h, ps in por_hash.items() if len(ps) > 1}
    if dups:
        print("\n⚠️  DUPLICATAS EXATAS (incluir apenas UMA cópia no PDF):")
        for ps in dups.values():
            print("   " + "  ==  ".join(p.name for p in ps))
    else:
        print("\n✅ Nenhuma duplicata exata.")

    print(f"\nTotal: {len(arquivos)} arquivos, {len(por_hash)} únicos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
