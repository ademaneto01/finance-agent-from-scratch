# Use official Python runtime as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# 👇 COPIA SÓ DEPENDÊNCIAS PRIMEIRO
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

# 👇 DEPOIS copia o código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]