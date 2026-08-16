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

# --reload watches for file changes — fine for local dev, not for production.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
