from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v123_market_regime_overlay_utils import (
    balanced_accuracy,
    load_market_regime_rows,
    zscore,
)


@dataclass(slots=True)
class V123JCpoMarketRegimeOverlayYearHoldoutAuditReport:
    summary: dict[str, Any]
    year_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "year_rows": self.year_rows,
            "interpretation": self.interpretation,
        }


class V123JCpoMarketRegimeOverlayYearHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123JCpoMarketRegimeOverlayYearHoldoutAuditReport:
        selection_path = self.repo_root / "reports" / "analysis" / "v123h_cpo_market_regime_overlay_discovery_v1.json"
        with selection_path.open("r", encoding="utf-8") as handle:
            selection = json.load(handle)
        chosen_score_name = selection["summary"]["chosen_score_name"]

        rows = load_market_regime_rows(self.repo_root)
        features = {
            "000001_return": zscore([row["000001_return"] for row in rows]),
            "000300_return": zscore([row["000300_return"] for row in rows]),
            "399006_return": zscore([row["399006_return"] for row in rows]),
            "000001_turn_ratio_5": zscore([row["000001_turn_ratio_5"] for row in rows]),
            "000300_turn_ratio_5": zscore([row["000300_turn_ratio_5"] for row in rows]),
            "399006_turn_ratio_5": zscore([row["399006_turn_ratio_5"] for row in rows]),
            "board_avg_return": zscore([row["board_avg_return"] for row in rows]),
            "board_breadth": zscore([row["board_breadth"] for row in rows]),
            "board_turn_ratio_5": zscore([row["board_turn_ratio_5"] for row in rows]),
        }
        candidates: dict[str, np.ndarray] = {
            "broad_riskoff_contraction_score": (
                -0.22 * features["000001_return"]
                - 0.28 * features["000300_return"]
                - 0.28 * features["399006_return"]
                - 0.10 * features["000001_turn_ratio_5"]
                - 0.06 * features["000300_turn_ratio_5"]
                - 0.06 * features["399006_turn_ratio_5"]
            ),
            "market_board_double_weakness_score": (
                -0.20 * features["000001_return"]
                - 0.25 * features["000300_return"]
                - 0.25 * features["399006_return"]
                - 0.15 * features["board_avg_return"]
                - 0.10 * features["board_breadth"]
                - 0.05 * features["board_turn_ratio_5"]
            ),
            "liquidity_drought_regime_score": (
                -0.20 * features["000001_turn_ratio_5"]
                - 0.20 * features["000300_turn_ratio_5"]
                - 0.20 * features["399006_turn_ratio_5"]
                - 0.20 * features["board_turn_ratio_5"]
                - 0.10 * features["000300_return"]
                - 0.10 * features["399006_return"]
            ),
        }
        values = candidates[chosen_score_name]
        years = sorted({row["trade_date"][:4] for row in rows})
        year_rows: list[dict[str, Any]] = []
        scores: list[float] = []
        if len(years) < 2:
            summary = {
                "acceptance_posture": "freeze_v123j_cpo_market_regime_overlay_year_holdout_audit_v1",
                "chosen_score_name": chosen_score_name,
                "year_count": 0,
                "mean_test_balanced_accuracy": 0.0,
                "min_test_balanced_accuracy": 0.0,
                "evaluability": "not_evaluable_single_year_only",
                "recommended_next_posture": "triage_as_pooled_explanatory_or_wait_for_longer_history",
            }
            interpretation = [
                "V1.23J cannot perform year holdout because the available index bootstrap only covers a single year.",
                "This means the regime overlay can only be judged on pooled and chronology evidence for now, not on cross-year transfer.",
            ]
            return V123JCpoMarketRegimeOverlayYearHoldoutAuditReport(
                summary=summary,
                year_rows=[],
                interpretation=interpretation,
            )

        for holdout_year in years:
            train_idx = [i for i, row in enumerate(rows) if row["trade_date"][:4] != holdout_year]
            test_idx = [i for i, row in enumerate(rows) if row["trade_date"][:4] == holdout_year]
            if not train_idx or not test_idx:
                continue
            threshold = float(np.quantile(values[train_idx], 0.75))
            y_true = [rows[i]["regime_risk_label"] for i in test_idx]
            y_pred = [values[i] >= threshold for i in test_idx]
            score = balanced_accuracy(y_true, y_pred)
            scores.append(score)
            year_rows.append(
                {
                    "holdout_year": holdout_year,
                    "test_row_count": len(test_idx),
                    "threshold": round(float(threshold), 8),
                    "balanced_accuracy": round(float(score), 8),
                }
            )
        summary = {
            "acceptance_posture": "freeze_v123j_cpo_market_regime_overlay_year_holdout_audit_v1",
            "chosen_score_name": chosen_score_name,
            "year_count": len(year_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8) if scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(scores)), 8) if scores else 0.0,
            "evaluability": "evaluable",
            "recommended_next_posture": "three_agent_triage_market_regime_overlay_branch",
        }
        interpretation = [
            "V1.23J tests whether the regime overlay survives year holdout, which is the first crude proxy for changing macro background.",
            "This is not policy text yet, but it is the minimum anti-overfit check on the broad market overlay layer.",
        ]
        return V123JCpoMarketRegimeOverlayYearHoldoutAuditReport(
            summary=summary,
            year_rows=year_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123JCpoMarketRegimeOverlayYearHoldoutAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123JCpoMarketRegimeOverlayYearHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123j_cpo_market_regime_overlay_year_holdout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
