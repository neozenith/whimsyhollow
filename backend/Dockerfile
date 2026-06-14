# Cloud Run container for the FastAPI backend, which also serves the built React SPA.
# Build from the REPO ROOT context (frontend + backend both in scope):
#   docker build -f backend/Dockerfile -t whimsyhollow-backend:local .

# --- Stage 1: build the React SPA with bun ---
FROM oven/bun:1.3-slim AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY frontend/ ./
RUN bun run build   # -> /fe/dist

# --- Stage 2: the Python backend ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    STATIC_DIR=/app/frontend_dist

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Deps first (cached), then code.
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
COPY backend/src ./src
RUN uv sync --frozen --no-dev

# The built SPA — served by FastAPI from settings.static_dir (= /app/frontend_dist).
COPY --from=frontend /fe/dist ./frontend_dist

EXPOSE 8080
CMD ["sh", "-c", ".venv/bin/uvicorn whimsyhollow.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
