#!/usr/bin/env bash
# Build the customized OLT image on top of the prebuilt base.
#
#   ./build.sh              # run checks, then build light-olt:dev
#   ./build.sh check        # checks only (syntax + unit tests)
#
# Override without editing anything:
#   BASE_IMAGE=...  base image to extend (default: ghcr.io/abelperezr/olt-ls:0.0.1)
#   IMAGE_TAG=...   tag for the customized image (default: light-olt:dev)
set -euo pipefail
cd "$(dirname "$0")"

BASE_IMAGE="${BASE_IMAGE:-ghcr.io/abelperezr/olt-ls:0.0.1}"
IMAGE_TAG="${IMAGE_TAG:-light-olt:dev}"
PROXY_IMAGE="${PROXY_IMAGE:-ghcr.io/abelperezr/olt-proxy:0.0.1}"

check_public_tree() {
  # Guardrail: these directories belong to the base images and must never
  # end up in this public repo (or baked into the overlay by accident).
  local forbidden
  for forbidden in yang device-ext proxy/cap_allow; do
    if [[ -e "$forbidden" ]]; then
      echo "ERROR: restricted path must not be part of this overlay: $forbidden" >&2
      return 1
    fi
  done
}

run_checks() {
  check_public_tree
  PYTHONPATH=src python3 -m compileall -q src tests
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  bash -n build.sh
  echo "Checks passed."
}

case "${1:-build}" in
  check)
    run_checks
    ;;
  build)
    shift || true
    run_checks
    echo "Building $IMAGE_TAG from $BASE_IMAGE"
    docker build \
      --build-arg "OLT_BASE_IMAGE=$BASE_IMAGE" \
      --tag "$IMAGE_TAG" \
      "$@" \
      .
    echo "Built: $IMAGE_TAG"
    echo "Proxy: $PROXY_IMAGE (pulled and run separately)"
    ;;
  *)
    echo "Usage: ./build.sh [build|check] [docker build options]" >&2
    exit 2
    ;;
esac
