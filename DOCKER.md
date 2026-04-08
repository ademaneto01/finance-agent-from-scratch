# Docker Guide

This document explains how to run `finance-agent-from-scratch` with Docker and Docker Compose based on the current `Dockerfile` and `docker-compose.yml`.

## Overview

The Compose setup includes three services:

- `qdrant`: local Qdrant vector database
- `api`: FastAPI application exposed on port `8000`
- `create-collection`: one-off initialization container used to create the Qdrant collection

Default local endpoints:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Qdrant API: `http://localhost:6333`
- Qdrant dashboard: `http://localhost:6333/dashboard`

## What the Docker Image Does

The application image is built from `python:3.12-slim` and:

1. Installs system packages required for Python builds
2. Installs `uv`
3. Copies `pyproject.toml` and `uv.lock`
4. Runs `uv sync --frozen --no-dev`
5. Copies the project source code
6. Starts the API with:

```bash
uv run uvicorn main:app --app-dir /app/api --host 0.0.0.0 --port 8000
```

## Prerequisites

- Docker
- Docker Compose
- A valid `GROQ_API_KEY`

Optional, depending on your use case:

- `OPENAI_API_KEY`
- `GUARDRAILS_TOKEN`

## Environment Variables

For Docker usage, start from the Docker-specific template:

```bash
cp .env.docker .env
```

Then edit `.env` and provide the values you need.

Example:

```env
QDRANT_API_KEY=qdrant-api-key
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=
GUARDRAILS_TOKEN=
```

Notes:

- In Docker Compose, `QDRANT_URL` for the containers is set internally to `http://qdrant:6333`
- `QDRANT_API_KEY` defaults to `qdrant-api-key` if you do not override it
- The API will not be useful without `GROQ_API_KEY`

## Quick Start

### 1. Build the containers

```bash
docker compose build
```

### 2. Initialize the Qdrant collection

Run the one-off initialization service the first time you set up the stack, or anytime you want to recreate the collection.

```bash
docker compose --profile init up create-collection
```

What this does:

- starts `qdrant`
- waits for it to become healthy
- runs `python -m api.ingestion.create_collection`

If the collection already exists, the initialization script may recreate it depending on the script logic.

### 3. Start the application stack

```bash
docker compose up
```

Or in detached mode:

```bash
docker compose up -d
```

### 4. Test the API

Example request:

```bash
curl -X POST "http://localhost:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is Apple a good investment?",
    "limit": 3
  }'
```

You can also inspect the interactive docs at `http://localhost:8000/docs`.

## Common Commands

### Start and stop

```bash
docker compose up
docker compose up -d
docker compose down
docker compose down -v
```

### Logs

```bash
docker compose logs -f
docker compose logs -f api
docker compose logs -f qdrant
docker compose --profile init logs create-collection
```

### Rebuild

```bash
docker compose build
docker compose build --no-cache
```

### Run commands inside the API container

```bash
docker compose exec api bash
docker compose exec api python -m api.ingestion.create_collection
```

### Re-run only the collection initializer

```bash
docker compose --profile init run --rm create-collection
```

## Development Behavior

The `api` service mounts the local repository into the container:

```yaml
volumes:
  - .:/app
  - /app/.venv
```

This has two important effects:

- your local code changes are immediately visible inside the container
- the container keeps its own virtual environment in `/app/.venv`

If you change dependencies in `pyproject.toml` or `uv.lock`, rebuild the image:

```bash
docker compose build
```

## Persistence

Qdrant data is stored in the named volume `qdrant_storage`, so vectors remain available across restarts unless you remove volumes with:

```bash
docker compose down -v
```

## Troubleshooting

### Qdrant does not become healthy

```bash
docker compose logs qdrant
docker compose down -v
docker compose up
```

### The API cannot connect to Qdrant

```bash
docker compose ps
docker compose logs api
```

Check that:

- `qdrant` is healthy
- `QDRANT_API_KEY` matches in both services
- the API is using `http://qdrant:6333` internally

### Collection initialization fails

```bash
docker compose --profile init logs create-collection
docker compose --profile init run --rm create-collection
```

Also confirm that `.env` contains a valid `GROQ_API_KEY` if the initialization flow depends on model-backed components.

### Port `8000` or `6333` is already in use

Either stop the conflicting process or change the host-side port mapping in `docker-compose.yml`.

Examples:

- change `"8000:8000"` to `"8001:8000"`
- change `"6333:6333"` to `"6335:6333"`

## Production Notes

This Compose file is primarily suited for local development. Before using it in production, consider:

1. Using a production-ready `.env` with real secrets management
2. Restricting or removing exposed Qdrant ports if external access is not needed
3. Running behind a reverse proxy
4. Adding resource limits and monitoring
5. Reviewing whether bind mounts should be removed in favor of immutable images

## Setup Checklist

- [ ] Docker and Docker Compose are installed
- [ ] `.env` was created from `.env.docker`
- [ ] `GROQ_API_KEY` was configured
- [ ] `docker compose build` completed successfully
- [ ] `docker compose --profile init up create-collection` completed successfully
- [ ] `docker compose up` started the API and Qdrant
- [ ] `http://localhost:8000/docs` is reachable

For general project information, see `README.md`.
