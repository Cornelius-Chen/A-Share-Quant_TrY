from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)
from a_share_quant.strategy.v124x_commercial_aerospace_sentiment_leadership_layer_v1 import (
    V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer,
)


@dataclass(slots=True)
class V124YCommercialAerospaceRoleGrammarRefreshV2Report:
    summary: dict[str, Any]
    role_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_rows": self.role_rows,
            "interpretation": self.interpretation,
        }


class V124YCommercialAerospaceRoleGrammarRefreshV2Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V124YCommercialAerospaceRoleGrammarRefreshV2Report:
        core = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(self.repo_root).analyze()
        sentiment = V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer(self.repo_root).analyze()

        role_rows: list[dict[str, Any]] = []
        for row in core.control_core_rows:
            role_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "role_layer": "control_core",
                    "role_semantic": row["authority_semantic"],
                    "supporting_score": row["liquidity_amount_mean"],
                }
            )
        for row in core.confirmation_rows:
            role_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "role_layer": "confirmation",
                    "role_semantic": row["authority_semantic"],
                    "supporting_score": row["liquidity_amount_mean"],
                }
            )
        for row in sentiment.sentiment_leader_rows:
            role_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "role_layer": "sentiment_leadership",
                    "role_semantic": row["sentiment_semantic"],
                    "supporting_score": row["sentiment_heat_score"],
                }
            )
        mirror_leader_symbols = {row["symbol"] for row in sentiment.sentiment_leader_rows}
        for row in core.mirror_rows:
            if row["symbol"] in mirror_leader_symbols:
                continue
            role_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "role_layer": "mirror",
                    "role_semantic": row["authority_semantic"],
                    "supporting_score": row["liquidity_amount_mean"],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v124y_commercial_aerospace_role_grammar_refresh_v2",
            "control_core_count": len(core.control_core_rows),
            "confirmation_count": len(core.confirmation_rows),
            "sentiment_leadership_count": len(sentiment.sentiment_leader_rows),
            "mirror_count": len(core.mirror_rows) - len(mirror_leader_symbols.intersection({row['symbol'] for row in core.mirror_rows})),
            "authoritative_rule": "commercial_aerospace_role_grammar_now_has_a_distinct_sentiment_leadership_layer_separate_from_control_core",
        }
        interpretation = [
            "V1.24Y refreshes the commercial-aerospace role grammar so that name-driven emotion leaders no longer hide inside a generic mirror bucket.",
            "This keeps strong sentiment leaders visible for breadth and heat reading without letting them overwrite owner-level controls.",
            "The board now has four lawful layers: control core, confirmation, sentiment leadership, and mirror.",
        ]
        return V124YCommercialAerospaceRoleGrammarRefreshV2Report(
            summary=summary,
            role_rows=role_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124YCommercialAerospaceRoleGrammarRefreshV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124YCommercialAerospaceRoleGrammarRefreshV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124y_commercial_aerospace_role_grammar_refresh_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
