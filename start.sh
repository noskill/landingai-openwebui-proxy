#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="landing-ai-wrapper"
CONTAINER_NAME="landing-ai-wrapper"
PORT_MAPPING="9028:8080"
NETWORK_NAME="gitea_default"

if [[ -z "${LANDING_API_KEY:-}" ]]; then
  echo "LANDING_API_KEY is required" >&2
  exit 1
fi

BUILD_ARGS=()

docker build "${BUILD_ARGS[@]}" -t "${IMAGE_NAME}" .

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run -d \
  --name "${CONTAINER_NAME}" \
  --network "${NETWORK_NAME}" \
  -p "${PORT_MAPPING}" \
  -e LANDING_API_KEY="${LANDING_API_KEY}" \
  -e LANDING_API_URL="${LANDING_API_URL:-https://api.va.landing.ai/v1/ade/parse}" \
  -e LANDING_MODEL="${LANDING_MODEL:-}" \
  -e RETURN_CHUNKS="${RETURN_CHUNKS:-false}" \
  -e LANDING_TIMEOUT_SECONDS="${LANDING_TIMEOUT_SECONDS:-120}" \
  -e GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-600}" \
  "${IMAGE_NAME}"

echo "Started ${CONTAINER_NAME} on ${PORT_MAPPING} (network: ${NETWORK_NAME})"
