#!/bin/bash
set -e

echo "==> Pulling latest changes..."
git pull origin main

echo "==> Building and restarting containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Cleaning up unused images..."
docker image prune -f

echo "==> Done. R.U.N. is live."
