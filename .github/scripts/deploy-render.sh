#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Dispara o deploy de uma imagem Docker em um serviço do Render.
#
# Uso: RENDER_DEPLOY_HOOK_URL=... deploy-render.sh <IMAGEM:TAG>
#
# O Deploy Hook (URL secreta, uma por ambiente) é guardado como secret do
# GitHub Environment. O parâmetro imgURL diz ao Render qual tag da imagem
# implantar — assim staging e production recebem exatamente o mesmo artefato.
# ------------------------------------------------------------------------------
set -euo pipefail

IMAGE="${1:?informe a imagem (ex.: ghcr.io/dono/finix:sha-abc)}"
: "${RENDER_DEPLOY_HOOK_URL:?secret RENDER_DEPLOY_HOOK_URL não configurado neste ambiente}"

encoded_image="$(jq -rn --arg v "${IMAGE}" '$v | @uri')"

echo "▶ Solicitando deploy de ${IMAGE}"
status="$(curl -sS -o response.json -w '%{http_code}' -X POST \
  "${RENDER_DEPLOY_HOOK_URL}&imgURL=${encoded_image}")"

# 200 = deploy iniciado; 202 = enfileirado atrás de outro deploy em andamento.
if [[ "${status}" != "200" && "${status}" != "202" ]]; then
  echo "::error::Render recusou o deploy (HTTP ${status}): $(cat response.json)"
  exit 1
fi
echo "✔ Deploy aceito pelo Render (HTTP ${status}): $(cat response.json)"
rm -f response.json
