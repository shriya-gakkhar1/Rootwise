# Simulator assumptions

The S1 generator uses one-second UTC ticks and the `start_epoch` from the scenario.
Traffic starts at a 100 request/second API-gateway baseline, has a small sinusoidal
wave and seeded multiplicative noise, and follows topology edge fan-out factors.
Service latency is seeded log-normal noise; baseline errors are small but non-zero.

At the ground-truth onset, PostgreSQL held connections increase at the configured leak
rate. Pool wait rises above the configured utilisation threshold, while PostgreSQL CPU
and latency remain in their normal ranges. Error and latency waves follow dependency
edges with their configured delays and seeded streams. Logs are sampled, with both
structured and plain-text records, and threshold alerts intentionally repeat to model
naive alerting. The customer-api deployment event is a decoy and is not the cause.
