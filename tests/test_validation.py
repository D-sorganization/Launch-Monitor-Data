from __future__ import annotations

from launch_monitor_data.validation import validate_repository_data


def test_repository_data_passes_provenance_and_contract_validation() -> None:
    report = validate_repository_data()

    assert report.ok, "\n".join(report.errors)
    assert report.source_count >= 10
    assert report.comparison_count == 57
    assert report.errors == ()


def test_reference_only_sources_are_not_treated_as_redistributable() -> None:
    report = validate_repository_data()

    assert report.reference_only_count >= 5
    assert report.redistributable_count >= 2
