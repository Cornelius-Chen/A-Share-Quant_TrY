from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124t_commercial_aerospace_local_feed_universe_triage_v1 import (
    V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer,
)


SENTIMENT_KEYS = [
    "trend_return_20",
    "turnover_rate_f_mean",
    "volume_ratio_mean",
    "limit_heat_rate",
    "up_day_rate",
    "liquidity_amount_mean",
]


@dataclass(slots=True)
class V124XCommercialAerospaceSentimentLeadershipLayerReport:
    summary: dict[str, Any]
    sentiment_leader_rows: list[dict[str, Any]]
    sympathy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "sentiment_leader_rows": self.sentiment_leader_rows,
            "sympathy_rows": self.sympathy_rows,
            "interpretation": self.interpretation,
        }


class V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _z(self, rows: list[dict[str, Any]], key: str) -> dict[str, float]:
        mean = sum(row[key] for row in rows) / len(rows)
        var = sum((row[key] - mean) ** 2 for row in rows) / len(rows)
        std = math.sqrt(var) or 1.0
        return {row["symbol"]: (row[key] - mean) / std for row in rows}

    def analyze(self) -> V124XCommercialAerospaceSentimentLeadershipLayerReport:
        upstream = V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer(self.repo_root).analyze()
        rows = upstream.control_eligible_rows + upstream.confirmation_rows + upstream.mirror_rows
        candidate_pool = [
            row
            for row in rows
            if row["group"] in {"概念助推组", "同走势镜像组"}
        ]
        zmaps = {key: self._z(candidate_pool, key) for key in SENTIMENT_KEYS}

        scored_rows: list[dict[str, Any]] = []
        for row in candidate_pool:
            symbol = row["symbol"]
            sentiment_heat_score = (
                0.26 * zmaps["limit_heat_rate"][symbol]
                + 0.22 * zmaps["turnover_rate_f_mean"][symbol]
                + 0.18 * zmaps["volume_ratio_mean"][symbol]
                + 0.14 * zmaps["up_day_rate"][symbol]
                + 0.12 * zmaps["liquidity_amount_mean"][symbol]
                + 0.08 * zmaps["trend_return_20"][symbol]
            )
            scored_rows.append(
                {
                    **row,
                    "sentiment_heat_score": round(sentiment_heat_score, 6),
                }
            )

        scored_rows.sort(key=lambda r: r["sentiment_heat_score"], reverse=True)
        leader_rows: list[dict[str, Any]] = []
        sympathy_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(scored_rows):
            if idx == 0:
                leader_rows.append({**row, "sentiment_semantic": "sentiment_leader_primary"})
            elif idx < 5:
                leader_rows.append({**row, "sentiment_semantic": "sentiment_leader_support"})
            else:
                sympathy_rows.append({**row, "sentiment_semantic": "sympathy_or_secondary"})

        summary = {
            "acceptance_posture": "freeze_v124x_commercial_aerospace_sentiment_leadership_layer_v1",
            "candidate_pool_count": len(candidate_pool),
            "sentiment_leader_count": len(leader_rows),
            "sympathy_count": len(sympathy_rows),
            "authoritative_rule": "sentiment_leadership_may_confirm_heat_and_breadth_but_may_not_override_control_authority",
            "recommended_next_posture": "attach_sentiment_leadership_as_a_non_control_layer_in_role_grammar",
        }
        interpretation = [
            "V1.24X rescues the strongest A-share name stocks and emotion leaders from the undifferentiated mirror bucket.",
            "This keeps names like 航天发展 visible as real行情主导 while still blocking them from pretending to be industrial control owners.",
            "The layer is meant for heat transmission, breadth confirmation, and theme sentiment reading rather than lawful control authority.",
        ]
        return V124XCommercialAerospaceSentimentLeadershipLayerReport(
            summary=summary,
            sentiment_leader_rows=leader_rows,
            sympathy_rows=sympathy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124XCommercialAerospaceSentimentLeadershipLayerReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124x_commercial_aerospace_sentiment_leadership_layer_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
