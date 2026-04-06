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
class V123ICpoMarketRegimeOverlayTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V123ICpoMarketRegimeOverlayTimeSplitAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123ICpoMarketRegimeOverlayTimeSplitAuditReport:
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
        unique_dates = sorted({row["trade_date"] for row in rows})
        split_rows: list[dict[str, Any]] = []
        scores: list[float] = []
        for split_index in range(1, len(unique_dates)):
            train_dates = set(unique_dates[:split_index])
            test_dates = set(unique_dates[split_index:])
            train_idx = [i for i, row in enumerate(rows) if row["trade_date"] in train_dates]
            test_idx = [i for i, row in enumerate(rows) if row["trade_date"] in test_dates]
            if not train_idx or not test_idx:
                continue
            threshold = float(np.quantile(values[train_idx], 0.75))
            y_true = [rows[i]["regime_risk_label"] for i in test_idx]
            y_pred = [values[i] >= threshold for i in test_idx]
            score = balanced_accuracy(y_true, y_pred)
            scores.append(score)
            split_rows.append(
                {
                    "train_end_date": max(train_dates),
                    "test_start_date": min(test_dates),
                    "test_row_count": len(test_idx),
                    "threshold": round(float(threshold), 8),
                    "balanced_accuracy": round(float(score), 8),
                }
            )
        summary = {
            "acceptance_posture": "freeze_v123i_cpo_market_regime_overlay_time_split_audit_v1",
            "chosen_score_name": chosen_score_name,
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8) if scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(scores)), 8) if scores else 0.0,
            "recommended_next_posture": "year_holdout_audit_chosen_market_regime_overlay",
        }
        interpretation = [
            "V1.23I tests whether the chosen top-level regime candidate survives chronology instead of only explaining pooled drawdown windows.",
            "This is the minimum hurdle before treating the regime signal as more than hindsight attribution.",
        ]
        return V123ICpoMarketRegimeOverlayTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123ICpoMarketRegimeOverlayTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123ICpoMarketRegimeOverlayTimeSplitAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123i_cpo_market_regime_overlay_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
