🇧🇷 [Leia em Português](README.pt-br.md)

# Koru Bank — Full Stack Banking Assistant

Portfolio case that evolves the original Koru Bank prototype into a **full stack** application, with a React frontend, a FastAPI backend, session/conversation persistence, event-driven automations, tests, and an architecture prepared for future AI integration.

> **Important:** this project is an educational simulation. It does not perform real banking operations, must not receive real personal data, and does not implement production-grade banking authentication.
> Live demo: https://koru-bank.onrender.com/

## Highlights

- React + Vite with a responsive UI and a guided support flow
- FastAPI with typed schemas, CORS, and automatic OpenAPI documentation
- Real CPF (Brazilian tax ID) checksum validation for the demo flow
- Independent session per user; no global state shared across conversations
- Persistence via SQLite by default, with configuration ready for PostgreSQL/Supabase
- Deterministic, rule-based chatbot with testable intent classification
- Simulated balance lookup, transfer with confirmation, and human handoff
- High-value transfer guardrail that routes to manual review
- Event-driven automation with an audit trail
- Operational dashboard with metrics and recent events
- `ai/` layer ready to receive an AI provider, but **disabled in this version**
- Backend tests and a CI pipeline on GitHub Actions
- Docker setup to run frontend + backend with a single command

## Architecture

```text
React / Vite
    |
    | HTTP JSON
    v
FastAPI
    |
    +-- Session API
    +-- Chat API
    +-- Operations API
    |
    v
Conversation Service
    |
    +-- Rule Intent Classifier  <--- active
    +-- AI Provider Interface   <--- ready / disabled
    +-- Automation Service
    +-- Guardrails
    |
    v
SQLAlchemy
    |
    +-- SQLite (local)
    +-- PostgreSQL / Supabase (configurable)
```

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Available flows

### Existing customer

1. Starts a session with a valid fictitious CPF.
2. Provides a name in the chat.
3. Selects "I'm already a customer".
4. Can check a fictitious balance, simulate a transfer, or request human support.
5. Transfers above the demo threshold are routed to manual review.

### New customer

This flow only logs a **demo interest event**, with no additional data collected. In a real solution, this step would be replaced by onboarding/KYC integrated with appropriate services.

## Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 18, React Router, Vite |
| Backend | Python, FastAPI, Pydantic |
| Persistence | SQLAlchemy, SQLite; ready for PostgreSQL |
| Quality | Pytest, Vitest, GitHub Actions |
| Infra | Docker, Nginx |
| AI | Interface prepared; integration not active |

## Run with Docker

Prerequisite: Docker Desktop.

```bash
docker compose up --build
```

Access:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`

## Run locally without Docker

### Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Demo CPF

Use fictitious data only. An example of a mathematically valid CPF for testing is:

```text
529.982.247-25
```

The application validates the checksum digits. The backend does not store the CPF in plain text: the session only keeps a hash and a masked version. This **does not turn the flow into real banking authentication**.

## Main endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | API health and capabilities |
| POST | `/api/v1/sessions` | Creates a demo session |
| POST | `/api/v1/chat/start` | Starts/resumes a conversation |
| POST | `/api/v1/chat/messages` | Processes a message |
| GET | `/api/v1/operations/dashboard` | Operational metrics |

## AI: ready, but not connected in this version

The project does not present rules as if they were AI. The current implementation uses a deterministic classifier and exposes a clear boundary for future evolution:

```text
app/ai/base.py
app/ai/router.py
```

Once integrated, the LLM would act only on **intent interpretation/structured extraction**, while sensitive operations would remain controlled by the backend, with validation, confirmation, and guardrails.

See the roadmap in [`docs/AI_ROADMAP.md`](docs/AI_ROADMAP.md).

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install
npm test
```

## What this case demonstrates

This repository was structured to showcase skills beyond the visual interface: separation of concerns, API design, state modeling, persistence, validation, automation, guardrails, basic observability, testing, CI, and preparation for AI features without coupling business rules to the model.

See also [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) for technical decisions and interview talking points.
