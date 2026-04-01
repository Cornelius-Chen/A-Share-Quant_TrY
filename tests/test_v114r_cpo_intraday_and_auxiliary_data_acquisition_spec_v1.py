from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114r_cpo_intraday_and_auxiliary_data_acquisition_spec_v1 import (
    V114RCpoIntradayAndAuxiliaryDataAcquisitionSpecAnalyzer,
)


def test_v114r_cpo_intraday_and_auxiliary_data_acquisition_spec() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114RCpoIntradayAndAuxiliaryDataAcquisitionSpecAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    assert result.summary["research_objective"] == "maximize_capture_of_diffusion_style_main_uptrend_while_containing_unnecessary_drawdown"
    assert any(row["field_group"] == "turnover_rate" for row in result.should_have_rows)
    assert any(row["gap_name"] == "no_intraday_raw_bars_present" for row in result.current_gap_rows)
