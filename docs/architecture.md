# Initial architecture

RootWise is a modular monolith. The backend owns the API and relational evidence
schema, the simulator owns deterministic topology and scenario specifications, and
the evaluation package owns offline metric definitions. The frontend is a thin
console shell that reads the backend health endpoint.

Future pipeline packages are intentionally empty extension points. No detection,
correlation, root-cause ranking, or LLM behavior is part of this skeleton.
