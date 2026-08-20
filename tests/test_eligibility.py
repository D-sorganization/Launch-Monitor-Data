from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from launch_monitor_data import eligibility


def _write_metadata(tmp_path: Path) -> Path:
    checkout = tmp_path / "checkout"
    authority = checkout / "data" / "authority"
    authority.mkdir(parents=True)
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    output = checkout / "results" / "v2"
    output.mkdir(parents=True)
    matrix = output / "source_metric_eligibility.csv"
    with matrix.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=eligibility.SAFE_ELIGIBILITY_FIELDS,
        )
        writer.writeheader()
        row = {field: "" for field in eligibility.SAFE_ELIGIBILITY_FIELDS}
        row.update(
            {
                "source_id": "traceable-source",
                "vendor_key": "trackman",
                "metric": "carry_yd",
                "source_rows": "40",
                "rows_with_metric": "35",
                "rows_with_complete_model_inputs_and_metric": "35",
                "agreement_eligible": "True",
                "agreement_reason": "eligible",
                "vendor_training_eligible": "False",
                "vendor_training_reason": "no_approved_repeating_split_group",
                "within_player_eligible": "False",
                "within_player_reason": "no_trusted_player_identifier",
            }
        )
        for field in eligibility.BOOLEAN_FIELDS:
            row.setdefault(field, "False")
            if row[field] == "":
                row[field] = "False"
        writer.writerow(row)
    matrix_hash = hashlib.sha256(matrix.read_bytes()).hexdigest()
    capability = {
        "schema": "launch-monitor-capability-manifest/v1",
        "policy_sha256": "a" * 64,
        "source_rows": 40,
        "strict_model_input_rows": 35,
        "eligibility_detail": "source_metric_eligibility.csv",
        "artifact_status": {"vendor_surrogate_training": "unavailable"},
        "vendors": [
            {
                "vendor_key": "trackman",
                "rows": 40,
                "strict_model_input_rows": 35,
                "allowed_operations": {
                    "model_agreement": True,
                    "vendor_training": False,
                    "within_player": False,
                },
                "training_blocker_messages": ["no_approved_repeating_split_group"],
            }
        ],
    }
    capability_path = output / "capability_manifest.json"
    capability_path.write_text(json.dumps(capability), encoding="utf-8")
    qualification = {
        "schema": "launch-monitor-data-qualification-manifest/v1",
        "source_rows": 40,
        "source_count": 1,
        "model_input_rows": 35,
        "policy_sha256": "a" * 64,
        "output_sha256": {
            "capability_manifest.json": hashlib.sha256(
                capability_path.read_bytes()
            ).hexdigest(),
            "source_metric_eligibility.csv": matrix_hash,
        },
    }
    (output / "qualification_manifest.json").write_text(
        json.dumps(qualification), encoding="utf-8"
    )
    release_b = checkout / "results" / "release_b"
    release_b.mkdir(parents=True)
    schedule_path = release_b / "confirmatory_schedule.csv"
    schedule_fields = (
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
    clubs = ("driver", "7-iron", "wedge")
    with schedule_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=schedule_fields)
        writer.writeheader()
        for index in range(252):
            club = clubs[index // 84]
            writer.writerow(
                {
                    "campaign_id": "release-b-test",
                    "shot_pair_id": f"pair-{index:03d}",
                    "trigger_id": f"trigger-{index:03d}",
                    "collection_block_id": f"{club}-block-{index // 14 + 1}",
                    "club_id": club,
                    "speed_band_id": f"{club}-locked",
                    "ball_model": "freeze-before-pilot",
                    "hitter_type": "robot",
                    "setting": "outdoor",
                    "impact_condition": "center",
                    "randomized_order": index + 1,
                }
            )
    ledger_path = release_b / "collection_ledger.csv"
    ledger_fields = (
        "shot_pair_id",
        "triggered",
        "synchronized",
        "calibrated",
        "reference_complete",
        "metric_complete",
        "analyzed",
        "primary_exclusion_reason",
    )
    with ledger_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=ledger_fields)
        writer.writeheader()
        for index in range(252):
            writer.writerow(
                {
                    "shot_pair_id": f"pair-{index:03d}",
                    "triggered": "False",
                    "synchronized": "False",
                    "calibrated": "False",
                    "reference_complete": "False",
                    "metric_complete": "False",
                    "analyzed": "False",
                    "primary_exclusion_reason": "not_collected",
                }
            )
    status = {
        "schema": "release-b-collection-status/v1",
        "schedule_sha256": hashlib.sha256(schedule_path.read_bytes()).hexdigest(),
        "ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "confirmatory_ready": False,
        "accounting": {
            "planned_pairs": 252,
            "triggered_pairs": 0,
            "synchronized_pairs": 0,
            "calibrated_pairs": 0,
            "reference_complete_pairs": 0,
            "metric_complete_pairs": 0,
            "analyzed_pairs": 0,
            "exclusions": {"not_collected": 252},
        },
        "readiness": {
            "required_per_cell": 84,
            "analyzed_by_cell": {club: 0 for club in clubs},
            "confirmatory_ready": False,
        },
    }
    (release_b / "status.json").write_text(json.dumps(status), encoding="utf-8")
    return checkout


def test_capability_api_exposes_only_verified_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _write_metadata(tmp_path)
    monkeypatch.setattr(eligibility, "verify_locked_private_checkout", lambda: checkout)

    report = eligibility.load_capabilities()
    rows = eligibility.load_source_metric_eligibility(vendor_key="trackman")
    training = eligibility.vendor_operation("trackman", "vendor_training")
    agreement = eligibility.vendor_operation("trackman", "model_agreement")

    assert report["source_rows"] == 40
    assert len(rows) == 1
    assert rows[0]["source_rows"] == 40
    assert rows[0]["agreement_eligible"] is True
    assert training.allowed is False
    assert training.reasons == ("no_approved_repeating_split_group",)
    assert agreement.allowed is True
    assert agreement.reasons == ()


def test_capability_api_rejects_tampered_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _write_metadata(tmp_path)
    monkeypatch.setattr(eligibility, "verify_locked_private_checkout", lambda: checkout)
    (checkout / "results" / "v2" / "capability_manifest.json").write_text(
        "{}", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="hash mismatch"):
        eligibility.load_capabilities()


def test_unknown_vendor_or_operation_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _write_metadata(tmp_path)
    monkeypatch.setattr(eligibility, "verify_locked_private_checkout", lambda: checkout)
    missing = eligibility.vendor_operation("foresight", "vendor_training")
    unsupported = eligibility.vendor_operation("trackman", "device_emulation")
    assert not missing.allowed
    assert missing.reasons == ("vendor_not_in_capability_manifest",)
    assert not unsupported.allowed
    assert unsupported.reasons == ("operation_not_in_capability_manifest",)


def test_release_b_status_exposes_verified_aggregate_zero_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _write_metadata(tmp_path)
    monkeypatch.setattr(eligibility, "verify_locked_private_checkout", lambda: checkout)

    status = eligibility.load_release_b_status()

    assert status.planned_pairs == 252
    assert status.triggered_pairs == 0
    assert status.analyzed_pairs == 0
    assert status.not_collected_pairs == 252
    assert status.analyzed_by_cell == (("7-iron", 0), ("driver", 0), ("wedge", 0))
    assert not status.confirmatory_ready
    assert status.vendor_training_eligible_decisions == 0
    assert status.vendor_training_eligible_rows == 0


def test_release_b_status_rejects_tampered_schedule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = _write_metadata(tmp_path)
    monkeypatch.setattr(eligibility, "verify_locked_private_checkout", lambda: checkout)
    schedule = checkout / "results" / "release_b" / "confirmatory_schedule.csv"
    schedule.write_text("tampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schedule hash mismatch"):
        eligibility.load_release_b_status()
