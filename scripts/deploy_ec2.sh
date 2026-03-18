#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] docker command not found"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] docker compose plugin not found"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[INFO] .env file was missing, copied from .env.example"
fi

echo "[INFO] Building and starting mini-redis container..."
docker compose up -d --build

echo "[INFO] Current container status"
docker compose ps

echo "[INFO] Last 50 log lines"
docker compose logs --tail=50 mini-redis
