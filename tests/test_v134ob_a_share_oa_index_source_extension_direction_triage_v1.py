from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ob_a_share_oa_index_source_extension_direction_triage_v1 import (
    V134OBAShareOAIndexSourceExtensionDirectionTriageV1Analyzer,
)


def test_v134ob_index_source_extension_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OBAShareOAIndexSourceExtensionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "index_daily_source_extension_opened_for_downstream_reaudit"


def test_v134ob_index_source_extension_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OBAShareOAIndexSourceExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["raw_source_acquisition"]["direction"].startswith("retain_new_raw_index_source")
