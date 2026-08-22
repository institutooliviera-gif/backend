# Imagem do backend do Instituto Oliveira (FastAPI + MongoDB via Motor).
FROM python:3.12-slim

# Evita arquivos .pyc e força stdout/stderr sem buffer (logs aparecem na hora no `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# curl é usado apenas pelo HEALTHCHECK abaixo
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Permite que o Docker (e o docker-compose) saibam se o serviço está saudável,
# e é o que possibilita o restart automático em caso de falha (ver docker-compose.yml)
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=5 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["sh", "-c", "python -m app.utils.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]