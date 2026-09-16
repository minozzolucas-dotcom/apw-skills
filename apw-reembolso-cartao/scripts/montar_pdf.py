#!/usr/bin/env python3
"""Monta o PDF consolidado de reembolso do cartão APW Brasil.

Uso:
    python3 montar_pdf.py manifest.json [--preview pagina1,pagina2]

O manifest declara os blocos NA ORDEM em que devem aparecer. Ver
references/manifest-exemplo.json.

Dependências: pymupdf, pillow, pillow-heif
    pip install pymupdf pillow pillow-heif --break-system-packages
"""
import argparse
import json
import sys
from pathlib import Path

import fitz  # pymupdf
from PIL import Image, ImageOps

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:  # HEIC simplesmente não abrirá
    pass

A4 = fitz.paper_rect("a4")  # 595 x 842 pt
NAVY = (0x01 / 255, 0x2B / 255, 0x5E / 255)  # APW Navy #012B5E
CINZA = (0.35, 0.35, 0.35)
BANNER_PADRAO = [120, 30, 480, 130]  # x0, y0, x1, y1 — faixa da extensão do navegador
MARGEM = 40
TOPO_TEXTO = 46  # altura reservada para o cabeçalho da página de NF


def brl(v) -> str:
    if v is None:
        return ""
    return f"R$ {float(v):,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def limpar_banner(page: fitz.Page, box) -> None:
    """Cobre a faixa de banner/extensão com retângulo branco."""
    rect = fitz.Rect(*box)
    page.draw_rect(rect, color=None, fill=(1, 1, 1), overlay=True)


def add_pdf(dest: fitz.Document, bloco: dict) -> int:
    src = fitz.open(bloco["arquivo"])
    inicio = dest.page_count
    dest.insert_pdf(src)
    if bloco.get("limpar_banner"):
        box = bloco.get("banner_box", BANNER_PADRAO)
        paginas = bloco.get("banner_paginas")  # None = todas do bloco
        for i in range(inicio, dest.page_count):
            if paginas is None or (i - inicio) in paginas:
                limpar_banner(dest[i], box)
    src.close()
    return dest.page_count - inicio


def add_imagem(dest: fitz.Document, bloco: dict, tmp: Path) -> int:
    """Cria uma página A4 com cabeçalho + a imagem encaixada abaixo."""
    origem = Path(bloco["arquivo"])
    img = Image.open(origem)
    img = ImageOps.exif_transpose(img)  # cupom de celular vem girado
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    destino = tmp / (origem.stem + "_norm.jpg")
    img.save(destino, "JPEG", quality=88)

    page = dest.new_page(width=A4.width, height=A4.height)

    titulo = bloco.get("titulo")
    if not titulo:
        est = bloco.get("estabelecimento", "Comprovante")
        data = bloco.get("data", "")
        titulo = f"Nota Fiscal - {est}" + (f" ({data})" if data else "")
    sub_partes = [p for p in (bloco.get("categoria"), brl(bloco.get("valor"))) if p]
    subtitulo = " - ".join(sub_partes) if sub_partes else ""

    page.insert_text((MARGEM, MARGEM), titulo, fontname="hebo", fontsize=12, color=NAVY)
    if subtitulo:
        page.insert_text((MARGEM, MARGEM + 16), subtitulo, fontname="helv", fontsize=10, color=CINZA)

    area = fitz.Rect(
        MARGEM,
        MARGEM + TOPO_TEXTO,
        A4.width - MARGEM,
        A4.height - MARGEM,
    )
    page.insert_image(area, filename=str(destino), keep_proportion=True)
    return 1


def preview(doc_path: Path, paginas, saida: Path) -> list:
    doc = fitz.open(doc_path)
    gerados = []
    for n in paginas:
        idx = n - 1
        if 0 <= idx < doc.page_count:
            pix = doc[idx].get_pixmap(dpi=110)
            alvo = saida / f"preview_pag{n}.png"
            pix.save(alvo)
            gerados.append(alvo)
    doc.close()
    return gerados


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--preview", default="", help="páginas p/ renderizar em PNG, ex: 1,5")
    args = ap.parse_args()

    man = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    base = Path(args.manifest).parent
    saida = Path(man.get("pasta_saida", "/mnt/user-data/outputs"))
    saida.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/reembolso_apw")
    tmp.mkdir(exist_ok=True)

    dest = fitz.open()
    mapa = []
    for bloco in man["blocos"]:
        arq = Path(bloco["arquivo"])
        if not arq.is_absolute():
            bloco["arquivo"] = str((base / arq).resolve())
        if not Path(bloco["arquivo"]).exists():
            print(f"❌ arquivo não encontrado: {bloco['arquivo']}")
            return 1
        inicio = dest.page_count + 1
        if bloco["tipo"] == "pdf":
            n = add_pdf(dest, bloco)
        elif bloco["tipo"] == "imagem":
            n = add_imagem(dest, bloco, tmp)
        else:
            print(f"❌ tipo desconhecido: {bloco['tipo']}")
            return 1
        mapa.append((inicio, dest.page_count, Path(bloco["arquivo"]).name, bloco.get("rotulo", bloco["tipo"])))

    destino = saida / man["arquivo_saida"]
    dest.save(str(destino), garbage=4, deflate=True)
    total_paginas = dest.page_count
    dest.close()

    print(f"✅ PDF gerado: {destino}  ({total_paginas} páginas)\n")
    print(f"{'PÁGINAS':<12} {'ROTULO':<34} ARQUIVO")
    print("-" * 92)
    for ini, fim, nome, rotulo in mapa:
        faixa = f"{ini}" if ini == fim else f"{ini}-{fim}"
        print(f"{faixa:<12} {rotulo[:33]:<34} {nome}")

    total_form = man.get("total_formulario")
    soma = sum(float(b.get("valor") or 0) for b in man["blocos"])
    if total_form is not None:
        print(f"\nTOTALIZADOR do formulário: {brl(total_form)}")
        print(f"Soma dos valores declarados no manifest: {brl(soma)}")
        if abs(float(total_form) - soma) > 0.01:
            print(f"⚠️  DIVERGÊNCIA de {brl(abs(float(total_form) - soma))} — conferir antes de enviar.")
        else:
            print("✅ Bate.")

    if args.preview:
        paginas = [int(x) for x in args.preview.split(",") if x.strip()]
        for p in preview(destino, paginas, saida):
            print(f"🖼️  preview: {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
