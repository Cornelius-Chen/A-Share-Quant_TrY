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
class V123HCpoMarketRegimeOverlayDiscoveryReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V123HCpoMarketRegimeOverlayDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123HCpoMarketRegimeOverlayDiscoveryReport:
        rows = load_market_regime_rows(self.repo_root)
        y_true = np.asarray([row["regime_risk_label"] for row in rows], dtype=bool)

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

        candidate_rows: list[dict[str, Any]] = []
        for name, values in candidates.items():
            threshold = float(np.quantile(values, 0.75))
            y_pred = values >= threshold
            positives = values[y_true]
            negatives = values[~y_true]
            gap = float(positives.mean() - negatives.mean()) if len(positives) and len(negatives) else 0.0
            candidate_rows.append(
                {
                    "score_name": name,
                    "mean_gap_positive_minus_negative": round(float(gap), 8),
                    "q75_threshold": round(float(threshold), 8),
                    "q75_balanced_accuracy": round(float(balanced_accuracy(list(y_true), list(y_pred))), 8),
                }
            )

        chosen_row = max(
            candidate_rows,
            key=lambda row: (row["q75_balanced_accuracy"], row["mean_gap_positive_minus_negative"]),
        )
        summary = {
            "acceptance_posture": "freeze_v123h_cpo_market_regime_overlay_discovery_v1",
            "sample_count": len(rows),
            "positive_count": int(y_true.sum()),
            "negative_count": int((~y_true).sum()),
            "chosen_score_name": chosen_row["score_name"],
            "chosen_gap": chosen_row["mean_gap_positive_minus_negative"],
            "chosen_q75_balanced_accuracy": chosen_row["q75_balanced_accuracy"],
            "recommended_next_posture": "time_split_audit_chosen_market_regime_overlay",
        }
        interpretation = [
            "V1.23H scans simple top-level regime scores built from broad index returns, liquidity contraction, and CPO board state.",
            "The purpose is to see whether major research-baseline drawdown windows are already legible from the regime layer before policy text or event timestamps are introduced.",
            "The next step is chronology audit on the best regime candidate.",
        ]
        return V123HCpoMarketRegimeOverlayDiscoveryReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123HCpoMarketRegimeOverlayDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123HCpoMarketRegimeOverlayDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123h_cpo_market_regime_overlay_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
