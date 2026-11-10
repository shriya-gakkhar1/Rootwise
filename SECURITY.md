# RootWise Security Checklist

This checklist is required for every feature, code modification, dependency update, and
deployment. A checklist item is only `PASS` when its behavior is verified by tests,
inspection, or an automated scan. Use `FAIL`, `PARTIAL`, `NOT APPLICABLE`, or
`NOT VERIFIED` when evidence does not support `PASS`.

## 1. API keys and secrets

- [ ] Status: `NOT VERIFIED` — No credentials, API keys, tokens, or passwords are hardcoded.
- [ ] Status: `PASS` — Secrets are injected through environment-specific secret management.
- [ ] Status: `PASS` — `.env` files are excluded by `.gitignore`.
- [ ] Status: `NOT VERIFIED` — Secrets are absent from frontend bundles, logs, responses, and Git history.
- [ ] Status: `NOT VERIFIED` — Any exposed credential has been rotated.

## 2. Environment configuration

- [ ] Status: `PARTIAL` — Development and production configuration are separated; production rejects development database settings.
- [ ] Status: `NOT VERIFIED` — Production debug mode is disabled.
- [ ] Status: `PARTIAL` — Required database configuration is validated at startup.
- [ ] Status: `NOT VERIFIED` — Internal configuration and stack traces are not exposed.

## 3. Authentication

- [ ] Status: `NOT APPLICABLE` — No user authentication or account API is implemented yet.
- [ ] Status: `NOT VERIFIED` — Passwords use Argon2id or another approved password hash when authentication is added.
- [ ] Status: `NOT VERIFIED` — Sessions/tokens expire and logout invalidates them.

## 4. Authorization and access control

- [ ] Status: `NOT APPLICABLE` — No privileged business API exists yet.
- [ ] Status: `NOT VERIFIED` — Backend RBAC, ownership checks, IDOR protection, and privilege-escalation tests are required before such APIs ship.

## 5. Input validation and XSS

- [ ] Status: `PARTIAL` — FastAPI/Pydantic validation is available for future request models; no business input API exists.
- [ ] Status: `PASS` — The migration and health query use fixed SQL/SQLAlchemy operations.
- [ ] Status: `NOT VERIFIED` — Output encoding, uploads, and form protections are not applicable or implemented.

## 6. API security

- [ ] Status: `NOT VERIFIED` — CORS, rate limiting, content-type enforcement, and sensitive endpoint protection are not configured.
- [ ] Status: `NOT VERIFIED` — Production error responses are safely redacted.

## 7. HTTP security

- [ ] Status: `NOT VERIFIED` — Security headers and CSP are not configured.
- [ ] Status: `NOT VERIFIED` — HTTPS enforcement and secure cookies are not applicable until browser authentication exists.

## 8. Database security

- [ ] Status: `PARTIAL` — SQLAlchemy operations are parameterized and production rejects development/loopback database settings.
- [ ] Status: `NOT VERIFIED` — Least-privilege database roles, encryption, sensitive-field handling, and access isolation require deployment configuration.

## 9. Dependencies and packages

- [ ] Status: `PARTIAL` — JavaScript lockfile integrity metadata exists.
- [ ] Status: `FAIL` — A Vite/esbuild advisory was reported by `npm audit`; upgrade and verify before exposing the dev server.
- [ ] Status: `NOT VERIFIED` — Python dependency scanning requires `pip-audit` or equivalent in CI.

## 10. Exposed files and information

- [ ] Status: `PASS` — `.env`, virtual environments, caches, dependencies, and frontend build output are ignored.
- [ ] Status: `NOT VERIFIED` — Public hosting, bundles, backups, and deployed API responses require deployment review.

## 11. Git and repository security

- [ ] Status: `PARTIAL` — No committed `.env` was found in the audited working tree; most application files are untracked and require review before the first commit.
- [ ] Status: `NOT VERIFIED` — Complete historical secret scanning and remote push protection are not configured.
- [ ] Status: `PASS` — No Git history was rewritten by this audit.

## 12. RootWise-specific security

- [ ] Status: `NOT APPLICABLE` — LLM investigation and remediation APIs are not implemented.
- [ ] Status: `NOT VERIFIED` — Future ingestion must isolate untrusted logs from instructions and cite evidence IDs for every claim.
- [ ] Status: `NOT VERIFIED` — Incident history, replay, simulation authorization, audit logging, dry-run remediation, and provider-key protection require implementation and tests.

## Required review evidence

For each completed checklist, record the command or test, date, scope, result, and any
remaining limitation. Never print secret values in evidence. Rotate any credential that
may have been exposed, even if it was intended for local development.
