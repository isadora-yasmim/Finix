#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Smoke test da aplicação no ar (teste dinâmico pós-deploy).
#
# Uso: smoke-test.sh <BASE_URL> <COMMIT_ESPERADO> [TIMEOUT_SEGUNDOS]
#
# 1. Espera /health/version responder com o commit esperado — garante que a
#    versão no ar é exatamente a que acabou de ser implantada (e não a anterior).
# 2. Verifica liveness (/health), banco (/health/db), frontend (/) e docs (/docs).
#
# Usado em três pontos da pipeline: no container recém-buildado (CI), após o
# deploy em staging e após o deploy em production.
# ------------------------------------------------------------------------------
set -euo pipefail

BASE_URL="${1:?informe a URL base}"
EXPECTED_SHA="${2:?informe o commit esperado}"
TIMEOUT="${3:-600}"
BASE_URL="${BASE_URL%/}"

echo "▶ Aguardando ${BASE_URL} servir o commit ${EXPECTED_SHA:0:7} (timeout ${TIMEOUT}s)..."
deadline=$((SECONDS + TIMEOUT))
current=""
while (( SECONDS < deadline )); do
  current="$(curl -fsS --max-time 10 "${BASE_URL}/health/version" 2>/dev/null | jq -r '.commit' 2>/dev/null || true)"
  if [[ "${current}" == "${EXPECTED_SHA}" ]]; then
    echo "✔ Versão correta no ar: ${current:0:7}"
    break
  fi
  echo "  ...ainda não (no ar: ${current:-sem resposta}). Nova tentativa em 10s."
  sleep 10
done
if [[ "${current}" != "${EXPECTED_SHA}" ]]; then
  echo "::error::Timeout: ${BASE_URL} não passou a servir o commit ${EXPECTED_SHA}"
  exit 1
fi

check() {
  local name="$1" path="$2" filter="$3" expected="$4" got
  got="$(curl -fsS --max-time 15 "${BASE_URL}${path}" | jq -r "${filter}")"
  if [[ "${got}" != "${expected}" ]]; then
    echo "::error::${name}: esperado '${expected}', recebido '${got}' (${path})"
    exit 1
  fi
  echo "✔ ${name}"
}

check "API viva (/health)"        /health    '.status'   ok
check "Banco acessível (/health/db)" /health/db '.database' ok

# Frontend: a raiz devolve o index.html da SPA.
if curl -fsS --max-time 15 "${BASE_URL}/" | grep -q '<div id="root">'; then
  echo "✔ Frontend servido (/)"
else
  echo "::error::A raiz não devolveu o index.html do frontend"
  exit 1
fi

curl -fsS --max-time 15 -o /dev/null "${BASE_URL}/docs"
echo "✔ Documentação da API (/docs)"

echo "✅ Smoke test OK em ${BASE_URL}"
