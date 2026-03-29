from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_a_recheck import FeaturePackARecheckAnalyzer


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_feature_pack_a_recheck_detects_threshold_straddles(tmp_path: Path) -> None:
    dataset_config = {
        "regime": {"min_top_score": 2.5, "min_score_margin": 0.0},
        "trend": {
            "hierarchy": {
                "min_resonance_for_core": 0.55,
                "min_quality_for_late_mover": 0.55,
                "min_composite_for_non_junk": 0.55,
            }
        },
    }
    dataset_config_path = tmp_path / "dataset.yaml"
    dataset_config_path.write_text(
        "\n".join(
            [
                "regime:",
                "  min_top_score: 2.5",
                "  min_score_margin: 0.0",
                "trend:",
                "  hierarchy:",
                "    min_resonance_for_core: 0.55",
                "    min_quality_for_late_mover: 0.55",
                "    min_composite_for_non_junk: 0.55",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    timeline_config_path = tmp_path / "timeline.yaml"
    timeline_config_path.write_text(
        "\n".join(
            [
                "dataset:",
                f"  config_path: {dataset_config_path.as_posix()}",
                "comparison:",
                "  incumbent_candidate: shared_default",
                "  challenger_candidate: theme_strict_quality_branch",
                "candidates:",
                "  - candidate_name: shared_default",
                "    override: {}",
                "  - candidate_name: theme_strict_quality_branch",
                "    override:",
                "      regime:",
                "        min_top_score: 2.8",
                "      trend:",
                "        hierarchy:",
                "          min_resonance_for_core: 0.60",
                "          min_quality_for_late_mover: 0.65",
                "          min_composite_for_non_junk: 0.60",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    timeline_report_path = tmp_path / "timeline.json"
    _write_json(
        timeline_report_path,
        {
            "summary": {"symbol": "AAA"},
            "candidate_records": [
                {
                    "candidate_name": "shared_default",
                    "strategy_name": "mainline_trend_c",
                    "daily_records": [
                        {
                            "trade_date": "2024-01-10",
                            "assignment_layer": "late_mover",
                            "assignment_reason": "late_mover_quality_fallback",
                            "permission_allowed": True,
                            "approved_sector_id": "S1",
                        }
                    ],
                },
                {
                    "candidate_name": "theme_strict_quality_branch",
                    "strategy_name": "mainline_trend_c",
                    "daily_records": [
                        {
                            "trade_date": "2024-01-10",
                            "assignment_layer": "junk",
                            "assignment_reason": "fallback_to_junk",
                            "permission_allowed": False,
                            "approved_sector_id": None,
                        }
                    ],
                },
            ],
        },
    )

    cycle_report_path = tmp_path / "cycle.json"
    _write_json(
        cycle_report_path,
        {
            "summary": {"strategy_name": "mainline_trend_c"},
            "mechanism_rows": [
                {
                    "mechanism_type": "entry_suppression_avoidance",
                    "trigger_date": "2024-01-10",
                    "trigger_reason": "incumbent_opened_cycle_but_challenger_suppressed_entry",
                    "incumbent_cycle": {
                        "entry_date": "2024-01-10",
                        "exit_date": "2024-01-11",
                    },
                }
            ],
        },
    )

    stock_snapshots_path = tmp_path / "stock_snapshots.csv"
    stock_snapshots_path.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,expected_upside,drive_strength,stability,liquidity,late_mover_quality,resonance,concept_support,primary_concept_weight,concept_count,concept_concentration_ratio,leader_component_score,core_component_score,late_component_score,non_junk_composite_score",
                "2024-01-10,AAA,S1,Sector 1,0.61,0.58,0.60,0.57,0.60,0.59,0.72,0.80,2,0.60,0.594,0.5855,0.596,0.596",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    sector_snapshots_path = tmp_path / "sector_snapshots.csv"
    sector_snapshots_path.write_text(
        "\n".join(
            [
                "trade_date,sector_id,sector_name,persistence,diffusion,money_making,leader_strength,relative_strength,activity",
                "2024-01-10,S1,Sector 1,0.45,0.42,0.44,0.41,0.43,0.45",
                "2024-01-10,S2,Sector 2,0.20,0.20,0.20,0.20,0.20,0.20",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = FeaturePackARecheckAnalyzer().analyze(
        case_specs=[
            {
                "case_name": "suspect_case",
                "dataset_name": "theme_research_v4",
                "timeline_config_path": str(timeline_config_path),
                "timeline_report_path": str(timeline_report_path),
                "cycle_report_path": str(cycle_report_path),
                "stock_snapshots_csv": str(stock_snapshots_path),
                "sector_snapshots_csv": str(sector_snapshots_path),
            }
        ]
    )

    assert result.summary["feature_edge_row_count"] == 1
    row = result.case_rows[0]
    assert row["late_quality_straddle"] is True
    assert row["non_junk_straddle"] is True
    assert row["top_score_straddle"] is True
    assert row["concept_support"] == 0.72
