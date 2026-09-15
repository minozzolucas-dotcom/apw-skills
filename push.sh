#!/usr/bin/env bash
# ============================================================
# apw-skills / push.sh
# Commit + push em um comando só.
# ============================================================
# Uso:
#   ./push.sh                              → mensagem = timestamp automático
#   ./push.sh "adiciona apw-nova-skill"    → mensagem sua
# ============================================================
set -e

# vai para a pasta do próprio script (funciona chamado de qualquer lugar)
cd "$(dirname "$0")"

# mensagem opcional; default = timestamp
MSG="${1:-atualização automática $(date '+%Y-%m-%d %H:%M')}"

# adiciona tudo (respeitando o .gitignore)
git add -A

# se nada mudou, não commita
if git diff --cached --quiet; then
  echo "✓ Nada mudou. Nada a commitar."
  exit 0
fi

# resumo do que vai commitar (útil ver antes de subir)
echo "--------------------------------------------------------"
echo "Alterações que vão para o commit:"
echo "--------------------------------------------------------"
git diff --cached --stat
echo "--------------------------------------------------------"

git commit -m "$MSG"

# push (usa o remote padrão e a branch atual)
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git push origin "$BRANCH"

echo "✓ Enviado para origin/$BRANCH: \"$MSG\""
