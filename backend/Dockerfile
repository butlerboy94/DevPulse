# Backend container image, used by docker-compose.yml's "backend" service.
FROM python:3.13-slim

WORKDIR /app

# gcc + libpq-dev are needed to build psycopg2 (the Postgres driver) from source.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# `chmod -R go-w /app` strips write access for everyone except the file
# owner (root) from the whole mounted source tree before the server starts.
# Needed because docker-compose bind-mounts ./backend over /app for local
# hot-reload, and Docker Desktop's Windows/macOS bind-mount layer defaults
# everything to world-writable (777) regardless of what's checked into git —
# without this, the sandbox subprocess's unprivileged user (see
# app/services/sandbox.py) would still be able to overwrite the app's own
# source files despite not being root (the group-owner is also root, so
# both "group" and "other" write bits have to go, not just "other").
# `|| true` so a chmod hiccup never blocks the server from starting.
# --reload watches for file changes — fine for local dev, not for production.
CMD ["sh", "-c", "chmod -R go-w /app 2>/dev/null || true; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
