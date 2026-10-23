#!/usr/bin/env bash
set -euo pipefail

GO_IMAGE="golang:1.27.3-bookworm@sha256:5c3e9b43cfd3bb95c7937462e29d87ada57b481a96fa23ad0eb61778d7a00110"
GO_SDK_DIR="${GO_SDK_DIR:-$HOME/code/apache/airflow/go-sdk}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAG_DIR="$(cd "$PROJECT_DIR/../../dags/multilang/go" && pwd)"

docker run --rm --platform linux/arm64 -u "$(id -u):$(id -g)" \
  -e HOME=/tmp -e GOCACHE=/tmp/gocache -e GOMODCACHE=/tmp/gomod \
  -e GOTOOLCHAIN=local -e GOFLAGS=-mod=mod -e CGO_ENABLED=0 \
  -v "$GO_SDK_DIR":/go-sdk:ro \
  -v "$PROJECT_DIR":/project:ro \
  -v "$DAG_DIR":/dag \
  "$GO_IMAGE" \
  sh -euc '
    mkdir -p /tmp/build && cd /tmp/build
    cp /project/go.mod /project/go.sum /dag/main.go .
    go tool airflow-go-pack --goos linux --goarch arm64 --output /dag/go_etl . -- -trimpath
  '
