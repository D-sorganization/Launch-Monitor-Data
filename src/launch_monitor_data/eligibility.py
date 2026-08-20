"""Data-free capability and eligibility views from the locked private authority."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from launch_monitor_data.paths import (
    locked_private_commit,
    verify_locked_private_checkout,
)

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
RELEASE_B_STATUS_SCHEMA = "release-b-collection-status/v1"
RELEASE_B_CELLS = ("7-iron", "driver", "wedge")
RELEASE_B_SCHEDULE_FIELDS = (
    "campaign_id",
    "shot_pair_id",
    "trigger_id",
    "collection_block_id",
    "club_id",
    "speed_band_id",
    "ball_model",
    "hitter_type",
    "setting",
    "impact_condition",
    "randomized_order",
)
RELEASE_B_LEDGER_FIELDS = (
    "shot_pair_id",
    "triggered",
    "synchronized",
    "calibrated",
    "reference_complete",
    "metric_complete",
    "analyzed",
    "primary_exclusion_reason",
)
RELEASE_B_STAGES = (
    "triggered",
    "synchronized",
    "calibrated",
    "reference_complete",
    "metric_complete",
    "analyzed",
)


@dataclass(frozen=True)
class OperationEligibility:
    """Fail-closed vendor operation decision for application clients."""

    vendor_key: str
    operation: str
    allowed: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseBStatus:
    """Verified aggregate Release B state; contains no capture or schedule rows."""

    schema: str
    source_commit: str
    schedule_sha256: str
    ledger_sha256: str
    planned_pairs: int
    triggered_pairs: int
    synchronized_pairs: int
    calibrated_pairs: int
    reference_complete_pairs: int
    metric_complete_pairs: int
    analyzed_pairs: int
    not_collected_pairs: int
    required_per_cell: int
    analyzed_by_cell: tuple[tuple[str, int], ...]
    confirmatory_ready: bool
    eligibility_matrix_sha256: str
    vendor_training_eligible_decisions: int
    vendor_training_eligible_rows: int


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


def _read_release_b_csv(path: Path, expected: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(
            f"locked authority lacks Release B metadata: {path.name}"
        )
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"unsafe or unsupported Release B schema for {path.name}")
        return list(reader)


def _release_b_boolean(value: str, field: str) -> bool:
    if value not in {"True", "False"}:
        raise ValueError(f"invalid Release B boolean for {field}")
    return value == "True"


def load_release_b_status() -> ReleaseBStatus:
    """Load aggregate Release B progress after verifying private row artifacts."""
    checkout = verify_locked_private_checkout()
    output = checkout / "results" / "release_b"
    status_path = output / "status.json"
    if not status_path.is_file():
        raise FileNotFoundError("locked authority lacks Release B status metadata")
    status: dict[str, Any] = json.loads(status_path.read_text(encoding="utf-8"))
    if status.get("schema") != RELEASE_B_STATUS_SCHEMA:
        raise ValueError("unsupported private Release B status schema")
    schedule_path = output / "confirmatory_schedule.csv"
    ledger_path = output / "collection_ledger.csv"
    schedule_hash = _sha256(schedule_path) if schedule_path.is_file() else ""
    ledger_hash = _sha256(ledger_path) if ledger_path.is_file() else ""
    if schedule_hash != status.get("schedule_sha256"):
        raise ValueError("Release B schedule hash mismatch")
    if ledger_hash != status.get("ledger_sha256"):
        raise ValueError("Release B ledger hash mismatch")
    schedule = _read_release_b_csv(schedule_path, RELEASE_B_SCHEDULE_FIELDS)
    ledger = _read_release_b_csv(ledger_path, RELEASE_B_LEDGER_FIELDS)
    if len(schedule) != 252 or len(ledger) != 252:
        raise ValueError("Release B requires exactly 252 schedule and ledger rows")
    scheduled_pairs = {row["shot_pair_id"] for row in schedule}
    ledger_pairs = {row["shot_pair_id"] for row in ledger}
    if len(scheduled_pairs) != 252 or scheduled_pairs != ledger_pairs:
        raise ValueError("Release B schedule and ledger pair identities differ")
    club_by_pair = {row["shot_pair_id"]: row["club_id"] for row in schedule}
    club_counts = {
        club: sum(row["club_id"] == club for row in schedule)
        for club in RELEASE_B_CELLS
    }
    if club_counts != {club: 84 for club in RELEASE_B_CELLS}:
        raise ValueError("Release B schedule must contain 84 pairs per primary cell")
    stage_counts = {
        stage: sum(_release_b_boolean(row[stage], stage) for row in ledger)
        for stage in RELEASE_B_STAGES
    }
    analyzed_by_cell = {
        club: sum(
            club_by_pair[row["shot_pair_id"]] == club
            and _release_b_boolean(row["analyzed"], "analyzed")
            for row in ledger
        )
        for club in RELEASE_B_CELLS
    }
    exclusions: dict[str, int] = {}
    for row in ledger:
        reason = row["primary_exclusion_reason"]
        if reason:
            exclusions[reason] = exclusions.get(reason, 0) + 1
    accounting = status.get("accounting")
    readiness = status.get("readiness")
    if not isinstance(accounting, dict) or not isinstance(readiness, dict):
        raise ValueError("Release B status lacks accounting or readiness")
    expected_accounting = {
        "planned_pairs": len(ledger),
        **{f"{stage}_pairs": count for stage, count in stage_counts.items()},
        "exclusions": exclusions,
    }
    if accounting != expected_accounting:
        raise ValueError("Release B accounting differs from the verified ledger")
    expected_ready = all(count >= 84 for count in analyzed_by_cell.values())
    if readiness.get("required_per_cell") != 84:
        raise ValueError("Release B readiness threshold must be 84 per cell")
    if readiness.get("analyzed_by_cell") != analyzed_by_cell:
        raise ValueError("Release B cell readiness differs from the verified ledger")
    if readiness.get("confirmatory_ready") is not expected_ready:
        raise ValueError("Release B readiness flag differs from the verified ledger")
    if status.get("confirmatory_ready") is not expected_ready:
        raise ValueError("Release B top-level readiness flag is inconsistent")
    eligibility_path = checkout / "results" / "v2" / "source_metric_eligibility.csv"
    eligibility_hash = _sha256(eligibility_path)
    decisions = load_source_metric_eligibility()
    training = tuple(
        row for row in decisions if row["vendor_training_eligible"] is True
    )
    return ReleaseBStatus(
        schema=RELEASE_B_STATUS_SCHEMA,
        source_commit=locked_private_commit(),
        schedule_sha256=schedule_hash,
        ledger_sha256=ledger_hash,
        planned_pairs=len(ledger),
        triggered_pairs=stage_counts["triggered"],
        synchronized_pairs=stage_counts["synchronized"],
        calibrated_pairs=stage_counts["calibrated"],
        reference_complete_pairs=stage_counts["reference_complete"],
        metric_complete_pairs=stage_counts["metric_complete"],
        analyzed_pairs=stage_counts["analyzed"],
        not_collected_pairs=exclusions.get("not_collected", 0),
        required_per_cell=84,
        analyzed_by_cell=tuple(sorted(analyzed_by_cell.items())),
        confirmatory_ready=expected_ready,
        eligibility_matrix_sha256=eligibility_hash,
        vendor_training_eligible_decisions=len(training),
        vendor_training_eligible_rows=sum(
            cast(int, row["rows_with_complete_model_inputs_and_metric"])
            for row in training
        ),
    )


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
