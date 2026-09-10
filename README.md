# GrainFlow — Smart Procurement Platform

GrainFlow is a farmer- and buyer-focused procurement assistant for creating, storing, and tracking agricultural sell and buy requests through text or voice.

## Features

- Sell produce and create persistent request IDs.
- Buy produce and record delivery requirements.
- Track request details and status journeys, including cancelled and rejected requests.
- Browser voice input with speech recognition and optional text-to-speech.
- Python voice CLI using the same central access engine.
- Optional Gemini understanding with a local smart-parser fallback.
- Conversation support for completing missing details across messages.

## Architecture

The React/Vite frontend sends messages to FastAPI at `POST /api/message`. FastAPI calls `farmer-access/core/access_engine.py`, which tries the optional Gemini service, falls back to `smart_parser.py`, routes actions through `action_router.py`, and persists requests in `farmer-access/data/requests.json`.

## Technology

- Frontend: React, Vite, CSS
- Backend: FastAPI, Pydantic, Uvicorn
- Voice: Web Speech API and Python SpeechRecognition/audio packages
- AI: optional `google-generativeai`; local parsing works without credentials

## Project structure

```text
api/                  FastAPI application
frontend/             React/Vite application
farmer-access/
  core/               access engine, parser, validation, persistence
  actions/            request action router
  ai/                 optional Gemini integration
  voice/              Python voice assistant
  tests/              existing Python tests
requirements.txt      Python dependencies
```

## Setup

### Backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://127.0.0.1:8000`. Start the backend first.

## Environment variables

Create a local `.env` only if Gemini is desired:

```text
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.0-flash
```

Gemini is optional; no API key is required for the local parser and request flows.

## API

- `GET /` — service status
- `GET /api/health` — backend health
- `POST /api/message` — process a message

Example:

```json
{
  "message": "I want to sell 50 kg of tomatoes from Bhimavaram my name is Poorna",
  "session_id": "demo"
}
```

## Testing

Run the existing Python tests from the repository root:

```powershell
python -m pytest farmer-access/tests
```

Build the frontend:

```powershell
cd frontend
npm run build
```

## Limitations and future improvements

Request persistence is a local JSON store and is intended for demonstrations, evaluation, and small local deployments rather than concurrent production workloads. Speech recognition availability depends on browser permissions and platform support. Future versions could add authenticated users, a transactional database, real buyer/farmer matching, multilingual speech support, and deployment configuration.
# GrainFlow AI - Member 3

This module is responsible for AI Prediction and Queue Management.

## Responsibilities

1. Farmer arrival prediction
2. Queue length prediction
3. Waiting-time prediction
4. Procurement-centre congestion prediction
5. Smart appointment-slot recommendation
6. Explainable AI
7. AI prediction APIs

## Technology

- Python
- Pandas
- NumPy
- Scikit-learn
- TensorFlow/Keras
- SHAP
- FastAPI
