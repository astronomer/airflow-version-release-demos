#!/usr/bin/env bash
set -euo pipefail

NODE_IMAGE="node:24.21.0-trixie-slim@sha256:173f125896c3b47ddf056734c7ea789d04595a6a08769a8f78e0df642781fb66"
PNPM_VERSION="10.28.1"
TS_SDK_DIR="${TS_SDK_DIR:-$HOME/code/apache/airflow/ts-sdk}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAGS_DIR="$(cd "$PROJECT_DIR/../../dags/multilang" && pwd)"
ENTRIES="typescript/typescript_etl yaml/yaml_etl_typescript"

docker run --rm \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -v "$TS_SDK_DIR":/src/ts-sdk:ro \
  -v "$PROJECT_DIR":/host \
  -v "$DAGS_DIR":/dags \
  "$NODE_IMAGE" \
  bash -euo pipefail -c "
    corepack enable pnpm
    corepack prepare pnpm@$PNPM_VERSION --activate
    mkdir -p /build/app/src
    cp -r /src/ts-sdk /build/ts-sdk
    cp -r /host/package.json /host/pnpm-workspace.yaml /host/tsconfig.json /build/app/
    for entry in $ENTRIES; do cp /dags/\$entry.ts /build/app/src/; done
    if [ -f /host/pnpm-lock.yaml ]; then cp /host/pnpm-lock.yaml /build/app/; fi
    cd /build/ts-sdk
    pnpm install --frozen-lockfile
    pnpm run build
    cd /build/app
    if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; else pnpm install; fi
    pnpm run typecheck
    for entry in $ENTRIES; do
      name=\$(basename \$entry)
      pnpm exec airflow-ts-pack src/\$name.ts --outfile dist/\$name.min.mjs
      cp dist/\$name.min.mjs /dags/\$entry.min.mjs
      chown $(id -u):$(id -g) /dags/\$entry.min.mjs
    done
    cp pnpm-lock.yaml /host/pnpm-lock.yaml
    chown $(id -u):$(id -g) /host/pnpm-lock.yaml
  "
