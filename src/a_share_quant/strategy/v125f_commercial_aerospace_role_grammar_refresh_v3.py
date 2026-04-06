from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)
from a_share_quant.strategy.v125d_commercial_aerospace_sentiment_control_boundary_audit_v1 import (
    V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer,
)


@dataclass(slots=True)
class V125FCommercialAerospaceRoleGrammarRefreshV3Report:
    summary: dict[str, Any]
    role_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_rows": self.role_rows,
            "interpretation": self.interpretation,
        }


class V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125FCommercialAerospaceRoleGrammarRefreshV3Report:
        control_upstream = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(self.repo_root).analyze()
        boundary_upstream = V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer(self.repo_root).analyze()

        boundary_map = {row["symbol"]: row for row in boundary_upstream.boundary_rows}

        role_rows: list[dict[str, Any]] = []
        for row in control_upstream.control_core_rows:
            role_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "role_layer": "control_core",
                    "role_semantic": row["authority_semantic"],
                    "supporting_score": row["liquidity_amount_mean"],
                }
            )

        for row in control_upstream.confirmation_rows:
            boundary = boundary_map[row["symbol"]]
            if boundary["boundary_semantic"] == "boundary_risk":
                role_rows.append(
                    {
                        "symbol": row["symbol"],
                        "name": row["name"],
                        "role_layer": "sentiment_watch",
                        "role_semantic": "sentiment_watch_quarantine",
                        "supporting_score": boundary["sentiment_top_rate"],
                    }
                )
            else:
                role_rows.append(
                    {
                        "symbol": row["symbol"],
                        "name": row["name"],
                        "role_layer": "confirmation",
                        "role_semantic": row["authority_semantic"],
                        "supporting_score": row["liquidity_amount_mean"],
                    }
                )

        for row in control_upstream.mirror_rows:
            boundary = boundary_map[row["symbol"]]
            if boundary["boundary_semantic"] == "boundary_risk":
                role_rows.append(
                    {
                        "symbol": row["symbol"],
                        "name": row["name"],
                        "role_layer": "sentiment_watch",
                        "role_semantic": "sentiment_watch_quarantine",
                        "supporting_score": boundary["sentiment_top_rate"],
                    }
                )
            else:
                role_rows.append(
                    {
                        "symbol": row["symbol"],
                        "name": row["name"],
                        "role_layer": "mirror",
                        "role_semantic": "mirror_only",
                        "supporting_score": row["liquidity_amount_mean"],
                    }
                )

        layer_counts: dict[str, int] = {}
        for row in role_rows:
            layer_counts[row["role_layer"]] = layer_counts.get(row["role_layer"], 0) + 1

        role_rows.sort(key=lambda r: (r["role_layer"], -float(r["supporting_score"]), r["symbol"]))
        summary = {
            "acceptance_posture": "freeze_v125f_commercial_aerospace_role_grammar_refresh_v3",
            "control_core_count": layer_counts.get("control_core", 0),
            "confirmation_count": layer_counts.get("confirmation", 0),
            "sentiment_watch_count": layer_counts.get("sentiment_watch", 0),
            "mirror_count": layer_counts.get("mirror", 0),
            "000547_role_layer": next(row["role_layer"] for row in role_rows if row["symbol"] == "000547"),
            "authoritative_rule": "boundary_risk_names_remain_visible_as_sentiment_watch_quarantine_but_cannot_hold_control_or_free_sentiment_authority",
        }
        interpretation = [
            "V1.25F refreshes the commercial-aerospace role grammar after the sentiment-control boundary audit.",
            "The main change is that boundary-risk names no longer sit inside a free-standing sentiment leadership layer; they are moved into a quarantined sentiment-watch layer.",
            "This keeps names like 航天发展 visible for heat reading while still blocking them from lawful control authority or replay semantics.",
        ]
        return V125FCommercialAerospaceRoleGrammarRefreshV3Report(
            summary=summary,
            role_rows=role_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125FCommercialAerospaceRoleGrammarRefreshV3Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125f_commercial_aerospace_role_grammar_refresh_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
