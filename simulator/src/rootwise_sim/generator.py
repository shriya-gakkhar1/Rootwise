"""Deterministic S1 connection-pool exhaustion data generation."""

import csv
import hashlib
import itertools
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

from .graph import build_topology_graph
from .loader import load_scenario, load_topology
from .models import TopologySpec

GENERATOR_VERSION = "1.0.0"
_SERVICE_ORDER = (
    "frontend",
    "api-gateway",
    "auth-service",
    "customer-api",
    "order-service",
    "payment-service",
    "postgres",
    "queue",
)


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _streams(seed: int, services: list[str]) -> dict[tuple[str, str], np.random.Generator]:
    names = [name for name in _SERVICE_ORDER if name in services]
    root = np.random.SeedSequence(seed)
    service_sequences = root.spawn(len(names))
    result: dict[tuple[str, str], np.random.Generator] = {}
    for service, service_sequence in zip(names, service_sequences):
        signals = service_sequence.spawn(8)
        for signal, signal_sequence in zip(
            ("rate", "error", "latency", "cpu", "memory", "pool", "logs", "trace"),
            signals,
        ):
            result[(service, signal)] = np.random.default_rng(signal_sequence)
    return result


def _timestamp(start: datetime, tick: int) -> str:
    return (start + timedelta(seconds=tick)).isoformat().replace("+00:00", "Z")


def _baseline_rates(topology: TopologySpec, api_rate: float) -> dict[str, float]:
    graph = build_topology_graph(topology)
    rates = {service.name: 0.0 for service in topology.services}
    rates["api-gateway"] = api_rate
    rates["frontend"] = api_rate
    for service in nx.topological_sort(graph):
        if service == "api-gateway":
            continue
        if service == "frontend":
            continue
        predecessors = list(graph.predecessors(service))
        rates[service] = sum(
            rates[parent]
            * next(
                edge.fan_out_factor
                for edge in topology.depends_on
                if edge.from_service == parent and edge.to_service == service
            )
            for parent in predecessors
        )
    return rates


def _fault_stage(service: str) -> int | None:
    # These are dependency waves: the two database callers fail first, then
    # their graph dependents. Auth receives the gateway's retry load.
    return {
        "auth-service": 1,
        "customer-api": 2,
        "order-service": 3,
        "api-gateway": 4,
        "frontend": 5,
    }.get(service)


def _propagation_delays(topology: TopologySpec, cause: str) -> dict[str, int]:
    graph = build_topology_graph(topology)
    delays = {cause: 0}
    for service in graph:
        if service == cause:
            continue
        try:
            path = nx.shortest_path(graph, service, cause)
        except nx.NetworkXNoPath:
            continue
        delays[service] = sum(
            next(
                edge.propagation_delay_seconds
                for edge in topology.depends_on
                if edge.from_service == source and edge.to_service == target
            )
            for source, target in itertools.pairwise(path)
        )
    return delays


def _event_key(event: dict[str, Any]) -> tuple[str, int, int]:
    return (event["ts"], {"change": 0, "alert": 1, "log": 2}[event["source"]], event["_sequence"])


def generate_run(scenario_path: str | Path, out_dir: str | Path, seed: int | None = None) -> Path:
    """Generate an S1 run and return its output directory."""
    scenario_file = Path(scenario_path)
    topology_file = scenario_file.with_name("topology.yaml")
    scenario = load_scenario(scenario_file)
    topology = load_topology(topology_file)
    actual_seed = scenario.seed if seed is None else seed
    services = [service.name for service in topology.services]
    rng = _streams(actual_seed, services)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    start = datetime.fromisoformat(scenario.start_epoch)
    onset = scenario.ground_truth.true_onset_seconds
    fault = scenario.fault_injection
    baseline = _baseline_rates(topology, 100.0)
    propagation_delays = _propagation_delays(topology, fault.node)
    wave_jitter = {service: round(rng[(service, "pool")].normal(0, 1.5)) for service in services}
    records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    sequence = 0

    def add_event(event: dict[str, Any]) -> None:
        nonlocal sequence
        event["_sequence"] = sequence
        sequence += 1
        events.append(event)

    for tick in range(scenario.duration_seconds):
        ts = _timestamp(start, tick)
        slow_wave = 1.0 + 0.04 * np.sin(2 * np.pi * tick / 600)
        pool_util = min(
            0.99,
            0.4 + max(0, tick - onset) * fault.leak_rate_connections_per_second / fault.pool_size,
        )
        wait_ms = (
            25.0
            if pool_util <= fault.utilisation_threshold
            else 25.0 + ((pool_util - fault.utilisation_threshold) * 5000)
        )
        for service in services:
            rate_noise = 1.0 + rng[(service, "rate")].normal(0, 0.025)
            rate = max(0.01, baseline[service] * slow_wave * rate_noise)
            stage = _fault_stage(service)
            wave_delay = (
                propagation_delays.get(service, 0) + (stage or 0) * 15 + wave_jitter[service]
            )
            fault_age = tick - onset - wave_delay
            fault_factor = max(0.0, min(1.0, fault_age / 120.0)) if stage else 0.0
            base_error = 0.006 + abs(rng[(service, "error")].normal(0, 0.001))
            error = base_error + (0.12 + 0.05 * fault_factor) * fault_factor
            base_latency = 80.0 + 8.0 * (services.index(service) % 4)
            latency = float(rng[(service, "latency")].lognormal(np.log(base_latency), 0.08))
            if service == "postgres":
                latency = float(np.clip(latency, base_latency * 0.75, base_latency * 1.25))
            else:
                latency *= 1.0 + 3.0 * fault_factor
            cpu = 35.0 + rng[(service, "cpu")].normal(0, 2.0)
            memory = 48.0 + rng[(service, "memory")].normal(0, 1.5)
            if service == "postgres":
                cpu = float(np.clip(cpu, 25.0, 45.0))
            row = {
                "ts": ts,
                "tick": tick,
                "service": service,
                "request_rate": round(rate * (1.0 + 0.8 * fault_factor), 5),
                "error_rate": round(float(min(0.99, error)), 5),
                "latency_p95_ms": round(latency, 5),
                "cpu_pct": round(float(cpu), 5),
                "memory_pct": round(float(memory), 5),
                "db_pool_utilisation": round(pool_util if service == "postgres" else 0.0, 5),
                "db_pool_wait_ms": round(
                    wait_ms if service in {"postgres", "customer-api", "order-service"} else 0.0, 5
                ),
                "queue_depth": round(
                    max(0.0, 3.0 + 40.0 * fault_factor if service == "queue" else 2.0), 5
                ),
            }
            records.append(row)

            sample_count = max(1, int(rate * 0.035))
            for sample in range(sample_count):
                if rng[(service, "logs")].random() > 0.72:
                    continue
                trace_id = f"{int(rng[(service, 'trace')].integers(0, 2**63)):016x}"
                failed = fault_factor > 0.2 and rng[(service, "error")].random() < min(error, 0.8)
                message = (
                    "database timeout while loading order"
                    if failed and service == "order-service"
                    else ("request completed" if not failed else "request failed")
                )
                event: dict[str, Any] = {
                    "ts": ts,
                    "source": "log",
                    "level": "ERROR" if failed else "INFO",
                    "service": service,
                    "message": message,
                    "trace_id": trace_id,
                }
                if failed:
                    event["exception"] = "AcquireTimeoutError"
                    event["stack"] = "Traceback (most recent call last): ... pool.acquire()"
                if (sequence % 5) != 0:
                    event["format"] = "structured"
                else:
                    event["format"] = "plain"
                    event["message"] = f"{ts} {service} {event['level']}: {message}"
                add_event(event)

        # Naive threshold alerts deliberately repeat while a condition persists.
        if tick >= onset:
            for row in records[-len(services) :]:
                baseline_latency = 100.0
                if row["error_rate"] > 0.05 or row["latency_p95_ms"] > 2 * baseline_latency:
                    add_event(
                        {
                            "ts": ts,
                            "source": "alert",
                            "level": "WARNING",
                            "service": row["service"],
                            "message": "threshold exceeded for 30 seconds",
                            "rule": "error_rate > 5% or latency_p95_ms > 2x baseline",
                        }
                    )

        if tick == max(0, onset - 90):
            add_event(
                {
                    "ts": ts,
                    "source": "change",
                    "level": "INFO",
                    "service": scenario.decoy_deploy.service,
                    "message": scenario.decoy_deploy.description,
                    "change_type": "deploy",
                }
            )

    events.sort(key=_event_key)
    for event in events:
        event.pop("_sequence", None)
    events_path = out / "events.jsonl"
    with events_path.open("w", encoding="utf-8", newline="\n") as file:
        for event in events:
            file.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    metrics_path = out / "metrics.csv"
    columns = list(records[0])
    with metrics_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    ground_truth_path = out / "ground_truth.json"
    ground_truth_path.write_text(
        json.dumps(scenario.ground_truth.model_dump(), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    files = [events_path, metrics_path, ground_truth_path]
    manifest = {
        "scenario_id": scenario.scenario_id,
        "spec_hash": _json_hash(
            {
                "scenario": scenario.model_dump(mode="json"),
                "topology": topology.model_dump(mode="json"),
            }
        ),
        "seed": actual_seed,
        "generator_version": GENERATOR_VERSION,
        "file_hashes": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return out
