# whimsyhollow — backend

Minimal async FastAPI backend: a tiny JSON API plus serving of the built React SPA
from `../frontend/dist`.

## Endpoints

- `GET /api/health` → `{"status": "ok"}`
- `GET /api/me` → `{"email", "user_id", "environment", "roles"}` — identity derived from
  the IAP `X-Goog-Authenticated-User-Email` header (null when absent).

## Develop

```bash
make -C backend install     # uv sync
make -C backend dev         # uvicorn --reload on :8080
make -C backend ci          # lint + typecheck + test
```

When `../frontend/dist` is absent (local dev with Vite serving the UI via proxy) the API
still serves; the SPA catch-all is only registered when the dist directory exists.
