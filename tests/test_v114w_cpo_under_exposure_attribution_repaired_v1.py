from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114w_cpo_under_exposure_attribution_repaired_v1 import (
    V114WCpoUnderExposureAttributionRepairedAnalyzer,
    load_json_report,
)


def test_v114w_cpo_under_exposure_attribution_repaired() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114WCpoUnderExposureAttributionRepairedAnalyzer()
    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v114v_payload=load_json_report(repo_root / "reports/analysis/v114v_cpo_benchmark_integrity_review_v1.json"),
    )

    assert result.summary["primary_under_exposure_reading"] == "under_exposure_still_present_after_replay_integrity_repair"
    assert result.summary["strategy_curve_repaired"] > 1.0
