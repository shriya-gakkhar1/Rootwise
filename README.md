# RootWise

RootWise is an evidence-driven incident intelligence and root cause analysis platform.
This repository currently contains the runnable project skeleton only.

## Quickstart

1. Clone the repository and enter it.
2. Copy `backend/.env.example` to `backend/.env`.
3. Run `make install`.
4. Run `make db-up`.
5. Run `make migrate`.
6. Run `make test`.
7. Run `make lint`.
8. Run `make run-backend` in one terminal.
9. Run `make run-frontend` in another terminal.
10. Open the frontend URL printed by Vite.

The backend listens on `http://localhost:8000` and the frontend uses that URL by
default. Set `VITE_API_BASE_URL` to point the frontend at another backend.

## Scope

The repository deliberately does not implement anomaly detection, event correlation,
hypothesis scoring, or LLM integration yet.
