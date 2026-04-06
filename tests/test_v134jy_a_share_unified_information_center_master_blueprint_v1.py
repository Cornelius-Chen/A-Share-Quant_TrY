from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jy_a_share_unified_information_center_master_blueprint_v1 import (
    V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer,
)


def test_v134jy_information_center_blueprint_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer(repo_root).analyze()

    assert report.summary["module_count"] == 10
    assert report.summary["object_chain_stage_count"] == 8
    assert report.summary["maturity_stage_count"] == 5
    assert report.summary["present_module_count"] >= 7
    assert report.summary["research_grade_or_better_count"] >= 2
    assert report.summary["current_repo_maturity_floor"] == "mvp_plus_partial_research_foundation"


def test_v134jy_information_center_blueprint_module_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JYAShareUnifiedInformationCenterMasterBlueprintV1Analyzer(repo_root).analyze()
    rows = {row["module"]: row for row in report.module_rows}

    assert rows["identity_entity"]["current_repo_status"] == "present_foundational"
    assert rows["taxonomy_business"]["current_repo_status"] == "present_partial"
    assert rows["event_catalyst"]["current_repo_status"] == "present_partial"
    assert rows["quality_trust"]["current_repo_status"] == "missing"
    assert rows["attention_heat"]["current_repo_status"] == "present_research_grade"
