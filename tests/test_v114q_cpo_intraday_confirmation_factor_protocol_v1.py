from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114q_cpo_intraday_confirmation_factor_protocol_v1 import (
    V114QCpoIntradayConfirmationFactorProtocolAnalyzer,
)


def test_v114q_cpo_intraday_confirmation_factor_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114QCpoIntradayConfirmationFactorProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    assert result.summary["target_board_style"] == "diffusion_main_uptrend_board"
    assert result.summary["intraday_factor_count"] >= 5
    assert result.readiness_audit["minimum_build_scope"] == ["300308", "300502", "300757", "688498"]
