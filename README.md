# GESTOR_LS - Web Migration Scaffold

This repository contains the original desktop app and a new `backend/` and `frontend/` scaffolding to help migrate to a web application.

## What I added
- `backend/` - Minimal FastAPI app that uses the existing database layer.
  - `backend/main.py` - Endpoints for `clientes` (GET/POST/PUT/DELETE).
  - `backend/schemas.py` - Pydantic schemas for Cliente.
- `frontend/` - Basic static frontend (`index.html`) that calls the API.
- Updated `requirements.txt` to include `fastapi` and `uvicorn`.

## How to run (web)

1. Create a virtual environment and install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the backend server (quick):

```powershell
# Run (single command) - recommended for local development
.
start_web.bat

Or start the backend directly with uvicorn:

```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
```

This will start an API server on http://127.0.0.1:8000

3. Access the frontend

Because the backend serves the frontend at the root, simply open the URL below after starting the server:

http://127.0.0.1:8000/

Alternatively, you can serve `frontend/` separately:

```powershell
cd ..\frontend
python -m http.server 3000
```

Open http://127.0.0.1:3000 in your browser.

## Docker (build & run)

You can also build and run the entire app using Docker and docker-compose.

```powershell
docker compose build --progress=plain
docker compose up
```

The FastAPI app + frontend will be available at http://127.0.0.1:8000

## Frontend development (React)

If you want to work on the React frontend locally (hot-reload):

```powershell
cd frontend/react-app
npm install
npm run dev
```

The React dev server runs on http://127.0.0.1:3000 and will proxy requests to the API if you configure CORS or a proxy.

## Desktop (legacy) UI

The desktop UI has been moved to `legacy_desktop/`. To run the legacy desktop application, open and run:

```powershell
cd legacy_desktop
python main.py
```

You can also use `requirements-desktop.txt` to install the desktop-only dependencies, if needed.

## Next steps / recommendations
- Convert other CRUD modules into API endpoints (processos, tarefas, usuarios, anexos, pagamentos, etc.).
- Implement authentication (JWT) and re-use `crud_usuarios` for login endpoints.
- Replace the desktop GUI (`app_*`) with a modern front-end (React, Vue, SolidJS, Svelte). I can scaffold a React app if you prefer.
- Add OpenAPI docs and write tests for endpoints.

If you'd like, I can now:
1) Expand the API to include `processos` and `tarefas` endpoints.
2) Build a small React prototype (create-react-app or Vite) for the full UI.
3) Add JWT authentication and rework `crud_usuarios` to accept/return token-based auth.

Tell me which step you'd like next, and I'll implement it.
