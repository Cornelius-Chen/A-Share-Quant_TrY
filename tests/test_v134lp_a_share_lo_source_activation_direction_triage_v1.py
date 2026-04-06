from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lp_a_share_lo_source_activation_direction_triage_v1 import (
    V134LPAShareLOSourceActivationDirectionTriageV1Analyzer,
)


def test_v134lp_source_activation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LPAShareLOSourceActivationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["active_local_ingest_count"] == 7
    assert (
        report.summary["authoritative_status"]
        == "source_activation_complete_enough_to_freeze_as_local_real_ingest_base"
    )


def test_v134lp_source_activation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LPAShareLOSourceActivationDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["url_catalog_sources"] == "retain_as_catalogued_sources_pending_live_fetch_adapters"
