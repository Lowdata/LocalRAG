#!/bin/bash
if docker compose version >/dev/null 2>&1; then
    docker compose up
elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose up
else
    echo "Neither docker compose nor docker-compose found."
    exit 1
fi
