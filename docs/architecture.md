# Initial architecture

RootWise is a modular monolith. The backend owns the API and relational evidence
schema, the simulator owns deterministic topology and scenario specifications, and
the evaluation package owns offline metric definitions. The frontend is a thin console shell that reads the backend health endpoint. The backend
also provides a local-development-only structured log ingestion API. Ingestion validates
and normalizes simulator-compatible records, resolves services, persists evidence, and
uses deterministic event identities for idempotent replay.

Future pipeline packages are intentionally empty extension points. No detection,
correlation, root-cause ranking, or LLM behavior is part of this milestone. See
`docs/ingestion.md` for the ingestion API contract and limits.
