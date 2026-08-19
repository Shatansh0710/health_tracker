# Health Tracker

A client-server health tracker. The Flask API will own all calculations and validation; the frontend will render the state returned by the API.

## Current functionality

The project now includes:

- Flask backend in `backend/app.py`
- Vanilla frontend dashboard in `frontend/`
- CORS enabled for `/api/*`
- In-memory session state for the active goal and meal list
- Server-side nutrient scaling from mock per-gram food baselines
- Daily calorie budget and macro progress returned by the API
- `GET /api/state` for the complete calculated application state
- `POST /api/log-meal` and `DELETE /api/log-meal/:id`
- `PUT /api/fitness-goal` for Weight Loss/Maintenance/Muscle Gain target switching
- `PUT /api/vibe-check` for the session's Vibe Check toggle
- `GET /api/mock-scan` for mock image-upload autofill data
- Conditional over-budget modal driven by the server's `isOverBudget` flag

The frontend does not calculate nutrients, targets, or budget status. It renders the latest JSON state returned by the backend.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend\app.py
```

Open `http://127.0.0.1:5000` in a browser. The page should report that the API is ready.
