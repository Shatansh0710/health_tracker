# Health Tracker

A client-server health tracker. The Flask API will own all calculations and validation; the frontend will render the state returned by the API.

## Phase 1 setup

The initial scaffold includes:

- Flask backend in `backend/app.py`
- Vanilla frontend in `frontend/`
- CORS enabled for `/api/*`
- `GET /api/health` smoke-test endpoint

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend\app.py
```

Open `http://127.0.0.1:5000` in a browser. The page should report that the API is ready.
