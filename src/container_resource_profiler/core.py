from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

PROJECT = "container-resource-profiler"
REQUIRED_FIELDS = ["scenario","cpu_percent","memory_mb","io_mb","network_mb","startup_ms"]

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)

def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def build_profile(record: dict[str, Any]) -> dict[str, Any]:
    if not _text(record["scenario"]):
        raise ValueError("scenario is required")
    for key in ("cpu_percent", "memory_mb", "io_mb", "network_mb", "startup_ms"):
        if not _number(record[key]) or record[key] < 0:
            raise ValueError("resource metrics must be non-negative numbers")
    if record["cpu_percent"] > 100 or record["memory_mb"] <= 0 or record["startup_ms"] <= 0:
        raise ValueError("resource metrics exceed valid bounds")
    return {"scenario": record["scenario"], "cpu_percent": record["cpu_percent"], "memory_mb": record["memory_mb"], "total_transfer_mb": record["io_mb"] + record["network_mb"], "startup_ms": record["startup_ms"]}

def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    artifact: Any = None
    if missing:
        status = "blocked"
        reason = "missing required fields: " + ", ".join(missing)
    else:
        try:
            artifact = build_profile(record)
            status = "passed"
            reason = "build_profile completed"
        except (TypeError, ValueError, KeyError) as exc:
            status = "failed"
            reason = str(exc)
    receipt = {"project": PROJECT, "status": status, "reason": reason, "record": record, "profile": artifact}
    receipt["evidence_sha256"] = sha256(_canonical(receipt).encode()).hexdigest()
    return receipt

