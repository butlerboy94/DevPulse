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
# owner (root) from the whole copied-in source tree before the server
# starts. It matters less here than in the local dev setup (this Dockerfile
# COPYs the code in rather than bind-mounting it, so it isn't world-writable
# by default the way Docker Desktop's Windows/macOS bind-mount layer makes
# it) but is kept for defense in depth, since the sandbox subprocess's
# unprivileged user (see app/services/sandbox.py) should never be able to
# write to the app's own source regardless of how the image was built.
# `|| true` so a chmod hiccup never blocks the server from starting.
#
# No --reload here: this is the command a real cloud host (Railway, Render,
# etc.) runs when it builds and starts the image directly, and --reload's
# "watch the filesystem and restart on every change" behavior is a dev
# convenience with no purpose (and a small ongoing cost) in production.
# Local development still gets hot-reload — docker-compose.yml's own
# `command:` line overrides this CMD and adds --reload back for that case.
CMD ["sh", "-c", "chmod -R go-w /app 2>/dev/null || true; exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
