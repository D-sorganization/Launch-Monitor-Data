"""Data-free capability and eligibility views from the locked private authority."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from launch_monitor_data.paths import verify_locked_private_checkout

CAPABILITY_SCHEMA = "launch-monitor-capability-manifest/v1"
QUALIFICATION_SCHEMA = "launch-monitor-data-qualification-manifest/v1"
SAFE_ELIGIBILITY_FIELDS = (
    "source_id",
    "monitor",
    "vendor_key",
    "device_identity_status",
    "observation_kind",
    "source_commit",
    "redistribution_status",
    "license_spdx",
    "player_identity_trust",
    "session_time_trust",
    "environment_status",
    "metric",
    "unit",
    "role",
    "source_rows",
    "rows_with_metric",
    "rows_with_complete_model_inputs_and_metric",
    "agreement_eligible",
    "agreement_reason",
    "within_player_eligible",
    "within_player_reason",
    "longitudinal_eligible",
    "longitudinal_reason",
    "strokes_gained_eligible",
    "strokes_gained_reason",
    "vendor_training_eligible",
    "vendor_training_reason",
    "cross_device_eligible",
    "cross_device_reason",
    "public_output_eligible",
    "public_output_reason",
)
INTEGER_FIELDS = {
    "source_rows",
    "rows_with_metric",
    "rows_with_complete_model_inputs_and_metric",
}
BOOLEAN_FIELDS = {
    field for field in SAFE_ELIGIBILITY_FIELDS if field.endswith("_eligible")
}


@dataclass(frozen=True)
class OperationEligibility:
    """Fail-closed vendor operation decision for application clients."""

    vendor_key: str
    operation: str
    allowed: bool
    reasons: tuple[str, ...]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verified_metadata() -> tuple[dict[str, Any], Path]:
    checkout = verify_locked_private_checkout()
    output = checkout / "results" / "v2"
    qualification_path = output / "qualification_manifest.json"
    if not qualification_path.is_file():
        raise FileNotFoundError("locked authority lacks v2 qualification metadata")
    qualification: dict[str, Any] = json.loads(
        qualification_path.read_text(encoding="utf-8")
    )
    if qualification.get("schema") != QUALIFICATION_SCHEMA:
        raise ValueError("unsupported private qualification schema")
    hashes = qualification.get("output_sha256")
    if not isinstance(hashes, dict):
        raise ValueError("private qualification manifest has no output hashes")
    required = ("capability_manifest.json", "source_metric_eligibility.csv")
    for name in required:
        path = output / name
        if not path.is_file() or _sha256(path) != hashes.get(name):
            raise ValueError(f"private qualification metadata hash mismatch for {name}")
    capability: dict[str, Any] = json.loads(
        (output / "capability_manifest.json").read_text(encoding="utf-8")
    )
    if capability.get("schema") != CAPABILITY_SCHEMA:
        raise ValueError("unsupported private capability schema")
    if capability.get("eligibility_detail") != "source_metric_eligibility.csv":
        raise ValueError("capability manifest has an unsafe eligibility path")
    if capability.get("policy_sha256") != qualification.get("policy_sha256"):
        raise ValueError("capability and qualification policy hashes differ")
    if capability.get("source_rows") != qualification.get("source_rows"):
        raise ValueError("capability and qualification corpus counts differ")
    if capability.get("strict_model_input_rows") != qualification.get(
        "model_input_rows"
    ):
        raise ValueError("capability and qualification strict counts differ")
    return capability, output / "source_metric_eligibility.csv"


def load_capabilities() -> dict[str, Any]:
    """Load hash-verified aggregate capabilities; never returns shot rows."""
    capability, _ = _verified_metadata()
    return capability


def load_source_metric_eligibility(
    *, vendor_key: str | None = None, source_id: str | None = None
) -> tuple[dict[str, object], ...]:
    """Load the data-free source/metric policy matrix from the locked checkout."""
    _, path = _verified_metadata()
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != SAFE_ELIGIBILITY_FIELDS:
            raise ValueError(
                "private eligibility schema contains unsafe or unknown fields"
            )
        records: list[dict[str, object]] = []
        for raw in reader:
            if vendor_key is not None and raw["vendor_key"] != vendor_key:
                continue
            if source_id is not None and raw["source_id"] != source_id:
                continue
            record: dict[str, object] = dict(raw)
            for field in INTEGER_FIELDS:
                record[field] = int(raw[field])
            for field in BOOLEAN_FIELDS:
                if raw[field] not in {"True", "False"}:
                    raise ValueError(f"invalid eligibility boolean for {field}")
                record[field] = raw[field] == "True"
            records.append(record)
    return tuple(records)


def vendor_operation(vendor_key: str, operation: str) -> OperationEligibility:
    """Return an allowed decision or traceable fail-closed reasons."""
    capability = load_capabilities()
    vendors = capability.get("vendors")
    if not isinstance(vendors, list):
        raise ValueError("capability manifest vendors must be an array")
    vendor = next(
        (
            item
            for item in vendors
            if isinstance(item, dict) and item.get("vendor_key") == vendor_key
        ),
        None,
    )
    if vendor is None:
        return OperationEligibility(
            vendor_key, operation, False, ("vendor_not_in_capability_manifest",)
        )
    operations = vendor.get("allowed_operations")
    if not isinstance(operations, dict) or operation not in operations:
        return OperationEligibility(
            vendor_key, operation, False, ("operation_not_in_capability_manifest",)
        )
    allowed = operations[operation]
    if not isinstance(allowed, bool):
        raise ValueError("capability operation decision must be boolean")
    if allowed:
        return OperationEligibility(vendor_key, operation, True, ())
    if operation == "vendor_training":
        messages = vendor.get("training_blocker_messages", [])
        if isinstance(messages, list) and all(
            isinstance(item, str) for item in messages
        ):
            reasons = tuple(messages)
        else:
            raise ValueError("training blocker messages must be strings")
    else:
        reason_field = f"{operation}_reason"
        reasons = tuple(
            sorted(
                {
                    str(row[reason_field])
                    for row in load_source_metric_eligibility(vendor_key=vendor_key)
                    if reason_field in row and row[reason_field] != "eligible"
                }
            )
        )
    return OperationEligibility(
        vendor_key,
        operation,
        False,
        reasons or (f"{operation}_not_eligible",),
    )
