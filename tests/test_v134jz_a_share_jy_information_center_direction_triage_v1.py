from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jz_a_share_jy_information_center_direction_triage_v1 import (
    V134JZAShareJYInformationCenterDirectionTriageV1Analyzer,
)


def test_v134jz_information_center_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JZAShareJYInformationCenterDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["module_count"] == 10
    assert report.summary["priority_row_count"] == 5
    assert (
        report.summary["authoritative_status"]
        == "treat_information_center_as_next_foundational_program_and_build_identity_event_quality_layers_before_shadow_binding"
    )


def test_v134jz_information_center_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JZAShareJYInformationCenterDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["priority_band"]: row["direction"] for row in report.triage_rows[:2]}

    assert directions["p0"] == "build_security_master_entity_alias_map_business_reference_and_concept_purity_first"
