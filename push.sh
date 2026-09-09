#!/bin/bash
set -e

REPO="https://github.com/minozzolucas-dotcom/apw-skills.git"
TMPDIR=$(mktemp -d)
ZIP="$HOME/Downloads/skills-apw-crm-20260909.zip"

echo ">>> Clonando repositório..."
git clone "$REPO" "$TMPDIR/apw-skills"
cd "$TMPDIR/apw-skills"

echo ">>> Descompactando skills..."
unzip -o "$ZIP" -d /tmp/skills-src

echo ">>> Copiando arquivos..."
cp -r /tmp/skills-src/skills-apw-crm/* .

echo ">>> Commit e push..."
git add -A
git commit -m "feat: skills APW CRM — reporte diário e calor do dia (09/09/2026)

- apw-reporte-crm-diario: build_report.py (formato oficial, 14 diretores) + collection_snippet.js
- apw-calor-do-dia: SKILL.md
- README com estrutura, instruções e tabela dos 14 GUIDs"
git push origin main

echo ""
echo "✅ Push concluído! Veja em: https://github.com/minozzolucas-dotcom/apw-skills"
