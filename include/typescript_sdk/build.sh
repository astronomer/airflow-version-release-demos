#!/usr/bin/env bash
set -euo pipefail

NODE_IMAGE="node:24.21.0-trixie-slim@sha256:173f125896c3b47ddf056734c7ea789d04595a6a08769a8f78e0df642781fb66"
PNPM_VERSION="10.28.1"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAGS_DIR="$(cd "$PROJECT_DIR/../../dags/multilang" && pwd)"
ENTRIES="typescript/typescript_etl yaml/yaml_etl_typescript"

docker run --rm \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -v "$PROJECT_DIR":/host:ro \
  -v "$DAGS_DIR":/dags \
  "$NODE_IMAGE" \
  bash -euo pipefail -c "
    corepack enable pnpm
    corepack prepare pnpm@$PNPM_VERSION --activate
    mkdir -p /build/app/src
    cp /host/package.json /host/pnpm-workspace.yaml /host/pnpm-lock.yaml /host/tsconfig.json /build/app/
    for entry in $ENTRIES; do cp /dags/\$entry.ts /build/app/src/; done
    cd /build/app
    pnpm install --frozen-lockfile
    pnpm run typecheck
    for entry in $ENTRIES; do
      name=\$(basename \$entry)
      pnpm exec airflow-ts-pack src/\$name.ts --outfile dist/\$name.min.mjs
      cp dist/\$name.min.mjs /dags/\$entry.min.mjs
      chown $(id -u):$(id -g) /dags/\$entry.min.mjs
    done
  "
