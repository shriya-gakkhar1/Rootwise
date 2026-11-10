# Log ingestion API

The first RootWise vertical slice accepts structured JSON logs in local and trusted
development environments. Ingestion routes are not registered when `ENV=production`;
authentication and authorization are required before this API can be exposed outside
that boundary.

## Limits and behavior

- Request bodies are limited to 1 MiB when a `Content-Length` is supplied.
- A batch contains 1 to 100 events.
- Service names are limited to 255 safe identifier characters.
- Messages are limited to 10,000 characters.
- Timestamps must include a timezone and are normalized to UTC.
- Severity values are normalized to `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.
  `WARN`, `ERR`, and `FATAL` are accepted aliases.
- Unknown services are registered with conservative `unknown` metadata.
- Duplicate identity is deterministic across service, timestamp, severity, message,
  trace, error signature, source, and span. Replays return `duplicates` without adding
  another database row.
- Raw validated JSON is retained as event provenance. Log text is never executed or
  interpreted as instructions.

## Single event

`POST /api/v1/events`

```json
{
  "service": "order-service",
  "ts": "2026-01-01T00:01:30Z",
  "level": "ERROR",
  "message": "database timeout while loading order",
  "trace_id": "0000000000000001",
  "exception": "AcquireTimeoutError"
}
```

Response:

```json
{
  "accepted": 1,
  "duplicates": 0,
  "event_ids": [1]
}
```

## Batch event

`POST /api/v1/events:batch`

```json
{
  "events": [
    {
      "ts": "2026-01-01T00:01:30Z",
      "service": "order-service",
      "level": "ERROR",
      "message": "database timeout while loading order",
      "trace_id": "0000000000000001",
      "exception": "AcquireTimeoutError"
    },
    {
      "ts": "2026-01-01T00:01:31Z",
      "service": "api-gateway",
      "level": "WARNING",
      "message": "threshold exceeded for 30 seconds"
    }
  ]
}
```

The simulator produces compatible records in `events.jsonl` through
`simulator/src/rootwise_sim/generator.py`.
