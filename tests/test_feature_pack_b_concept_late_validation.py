from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_b_concept_late_validation import (
    FeaturePackBConceptLateValidationAnalyzer,
    load_json_report,
)


def _write_timeline(
    path: Path,
    *,
    incumbent_pnls: list[float],
    challenger_pnls: list[float],
    repaired_dates: list[str],
) -> None:
    payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "daily_records": [],
                "fills": [],
                "closed_trades": [{"pnl": pnl} for pnl in incumbent_pnls],
            },
            {
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {
                        "trade_date": "2024-05-09",
                        "assignment_layer": "late_mover" if "2024-05-09" in repaired_dates else "junk",
                        "assignment_reason": "late_mover_quality_fallback",
                        "emitted_actions": ["buy"] if "2024-05-09" in repaired_dates else [],
                    },
                    {
                        "trade_date": "2024-06-26",
                        "assignment_layer": "late_mover" if "2024-06-26" in repaired_dates else "junk",
                        "assignment_reason": "late_mover_quality_fallback",
                        "emitted_actions": ["buy"] if "2024-06-26" in repaired_dates else [],
                    },
                ],
                "fills": [1] * (len(challenger_pnls) * 2),
                "closed_trades": [{"pnl": pnl} for pnl in challenger_pnls],
            },
        ]
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_feature_pack_b_concept_late_validation_closes_track_when_repairs_damage_alpha(tmp_path: Path) -> None:
    bridge_path = tmp_path / "bridge.json"
    baseline_path = tmp_path / "baseline.json"
    v2_path = tmp_path / "v2.json"
    v3_path = tmp_path / "v3.json"

    bridge_payload = {
        "summary": {"case_name": "theme_q2_002466_c"},
        "bridge_rows": [
            {"trigger_date": "2024-05-09"},
            {"trigger_date": "2024-06-26"},
        ],
    }
    bridge_path.write_text(json.dumps(bridge_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_timeline(
        baseline_path,
        incumbent_pnls=[-100.0, -200.0],
        challenger_pnls=[250.0, 200.0],
        repaired_dates=[],
    )
    _write_timeline(
        v2_path,
        incumbent_pnls=[-100.0, -200.0],
        challenger_pnls=[-20.0, 30.0],
        repaired_dates=["2024-05-09"],
    )
    _write_timeline(
        v3_path,
        incumbent_pnls=[-100.0, -200.0],
        challenger_pnls=[-40.0, 20.0],
        repaired_dates=["2024-05-09"],
    )

    result = FeaturePackBConceptLateValidationAnalyzer().analyze(
        bridge_payload=load_json_report(bridge_path),
        baseline_payload=load_json_report(baseline_path),
        baseline_challenger_name="theme_strict_quality_branch",
        variant_payloads=[
            ("v2", load_json_report(v2_path), "theme_strict_quality_branch"),
            ("v3", load_json_report(v3_path), "theme_strict_quality_branch"),
        ],
    )

    assert result.summary["acceptance_posture"] == "close_track_b_as_negative_informative"
    assert result.summary["all_tested_variants_degrade_alpha"] is True
    assert result.summary["all_tested_variants_remain_partial"] is True
    assert result.summary["best_variant_name"] == "v2"
