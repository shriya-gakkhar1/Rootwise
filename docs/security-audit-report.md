# RootWise Security Audit Report

**Audit type:** Read-only repository audit before remediation
**Date:** 2026-11-10
**Scope:** Backend, frontend, database/migrations, Compose/CI configuration, dependencies,
exposed files, and available Git history
**Method:** Static inspection and repository-local tests/scans only. No production or
external systems were contacted and no destructive security testing was performed.

## Executive summary

One confirmed high-severity configuration vulnerability was found. Docker Compose
contained a usable development database password and published PostgreSQL on all host
interfaces. The same development connection default was repeated in backend settings and
Alembic configuration. This could expose retained incident data and permit tampering when
the configuration is used outside an isolated local machine.

The fix now requires a password from the environment, binds the local database port to
loopback by default, removes the Alembic credential, requires `DATABASE_URL`, and rejects
known development credentials and loopback database hosts in production.

## Findings

### HIGH — Development database credential and public database binding

- **Affected files before remediation:** `docker-compose.yml`, `backend/.env.example`,
  `backend/src/rootwise/config.py`, `backend/alembic.ini`
- **Evidence:** Compose supplied a fixed PostgreSQL password and mapped `5432:5432`;
  backend settings and Alembic repeated the same usable connection string.
- **Risk:** A host able to reach TCP/5432 could authenticate, read or alter persistent
  database data, and tamper with evidence or audit records.
- **Remediation:** Require `POSTGRES_PASSWORD`, bind to `127.0.0.1` by default, remove
  the Alembic URL credential, require `DATABASE_URL`, and reject development passwords
  and loopback database hosts when `ENV=production`.
- **Verification:** `backend/tests/test_health.py` covers production rejection cases.
  Compose configuration was reviewed statically. A live database test was not run.
- **Status:** Remediated in source; deployment behavior remains `PARTIAL` until a
  deployment-specific review confirms secret injection and network policy.

## Dependency and supply-chain observations

- `npm audit --omit=dev` reported two advisories in the Vite/esbuild development-server
  dependency tree. This was not treated as a confirmed production remote exploit because
  the repository does not configure Vite to listen publicly, but the dependency requires
  upgrade and verification.
- `pip-audit --local` could not run because `pip-audit` was not installed. Python
  dependency vulnerability status is therefore `NOT VERIFIED`.

## Evidence gaps and unresolved vulnerabilities

Prioritized unresolved items:

1. **High:** Upgrade Vite/esbuild and verify with `npm audit`; do not expose the Vite
   development server externally.
2. **High:** Add authentication, backend authorization, ownership/IDOR protection, and
   security tests before adding incident or investigation APIs.
3. **High:** Add production TLS, explicit CORS, security headers/CSP, rate limiting,
   secure error handling, and deployment secret management.
4. **Medium:** Add Python dependency scanning (for example `pip-audit`) and CI secret
   scanning/push protection.
5. **Medium:** Define least-privilege database roles, encryption requirements, backup
   protection, and retention controls.
6. **Medium:** Implement prompt-injection isolation, evidence-cited LLM output, dry-run
   remediation approval, simulation authorization, and administrative audit logging
   before LLM/remediation features are enabled.

These are not marked as vulnerabilities in implemented code where the corresponding
feature does not exist; they are release blockers for future feature surfaces.

## Verification performed

- Read-only inspection of repository source, configuration, CI, frontend, migrations,
  dependency manifests, ignore rules, and the available Git history.
- Existing health and migration test structure reviewed.
- No production service, external target, or destructive database operation was tested.
- Secret values are intentionally omitted from this report.
