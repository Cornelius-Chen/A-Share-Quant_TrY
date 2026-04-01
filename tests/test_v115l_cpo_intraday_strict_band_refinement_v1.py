from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v115l_cpo_intraday_strict_band_refinement_v1 import (
    V115LCpoIntradayStrictBandRefinementAnalyzer,
)


def test_v115l_strict_band_refinement_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115LCpoIntradayStrictBandRefinementAnalyzer(repo_root=repo_root)
    report = analyzer.analyze(
        v115k_payload=json.loads((repo_root / "reports" / "analysis" / "v115k_cpo_intraday_band_action_audit_v1.json").read_text(encoding="utf-8"))
    )
    summary = report.summary
    assert summary["acceptance_posture"] == "freeze_v115l_cpo_intraday_strict_band_refinement_v1"
    assert summary["candidate_add_band_count_before_refinement"] == 3
    assert summary["strict_candidate_add_band_count"] >= 1
