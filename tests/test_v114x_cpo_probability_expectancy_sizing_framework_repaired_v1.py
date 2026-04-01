from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114w_cpo_under_exposure_attribution_repaired_v1 import (
    V114WCpoUnderExposureAttributionRepairedAnalyzer,
)
from a_share_quant.strategy.v114x_cpo_probability_expectancy_sizing_framework_repaired_v1 import (
    V114XCpoProbabilityExpectancySizingFrameworkRepairedAnalyzer,
    load_json_report,
)


def test_v114x_cpo_probability_expectancy_sizing_framework_repaired() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    repaired_under_exposure = V114WCpoUnderExposureAttributionRepairedAnalyzer().analyze(
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v114v_payload=load_json_report(repo_root / "reports/analysis/v114v_cpo_benchmark_integrity_review_v1.json"),
    )
    analyzer = V114XCpoProbabilityExpectancySizingFrameworkRepairedAnalyzer()
    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v114w_payload=repaired_under_exposure.as_dict(),
    )

    assert result.summary["framework_ready_for_replay_injection_next"] is True
    assert result.summary["recommended_strong_board_min_gross_exposure_repaired"] == 0.30
    assert any(row["source_family"] == "core_module_leader" for row in result.source_sizing_rows)
