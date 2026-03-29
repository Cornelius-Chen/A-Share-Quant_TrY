from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PermissionLossEdgeReport:
    summary: dict[str, Any]
    ranked_sector_scores: list[dict[str, Any]]
    candidate_evaluations: list[dict[str, Any]]
    action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "ranked_sector_scores": self.ranked_sector_scores,
            "candidate_evaluations": self.candidate_evaluations,
            "action_rows": self.action_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class PermissionLossEdgeAnalyzer:
    """Explain why one candidate loses permission on a borderline date."""

    def analyze(
        self,
        *,
        symbol: str,
        trade_date: str,
        ranked_sector_scores: list[dict[str, Any]],
        candidate_evaluations: list[dict[str, Any]],
        action_rows: list[dict[str, Any]],
    ) -> PermissionLossEdgeReport:
        top_score = ranked_sector_scores[0] if ranked_sector_scores else None
        second_score = ranked_sector_scores[1] if len(ranked_sector_scores) > 1 else None
        incumbent = next(
            (row for row in candidate_evaluations if row.get("role") == "incumbent"),
            None,
        )
        challenger = next(
            (row for row in candidate_evaluations if row.get("role") == "challenger"),
            None,
        )
        summary = {
            "symbol": symbol,
            "trade_date": trade_date,
            "top_sector": top_score,
            "second_sector": second_score,
            "candidate_count": len(candidate_evaluations),
            "action_row_count": len(action_rows),
            "dominant_rule": (
                "A permission split is promotion-relevant only when the top sector stays investable "
                "for the incumbent, fails the challenger threshold or path rule, and suppresses a real buy."
            ),
        }
        interpretation = [
            "This report is about one date edge, not the whole strategy. The key question is whether the challenger loses permission because the sector score falls below its own threshold, because the margin is too small, or because the regime path is held elsewhere.",
            "If the incumbent still emits a buy while the challenger does not, the permission edge is no longer abstract; it has crossed into a tradable state difference.",
            "A later position-gap exit should be treated as downstream evidence from this missed buy edge rather than as an independent first cause.",
        ]
        if top_score is not None and incumbent is not None and challenger is not None:
            incumbent_passes_top = bool(incumbent.get("permission_allowed"))
            challenger_passes_top = bool(challenger.get("permission_allowed"))
            if incumbent_passes_top and not challenger_passes_top:
                interpretation.append(
                    "On this date the incumbent keeps the top sector investable while the challenger rejects it; this is the exact permission-loss edge the next repair cycle should study."
                )

        return PermissionLossEdgeReport(
            summary=summary,
            ranked_sector_scores=ranked_sector_scores,
            candidate_evaluations=candidate_evaluations,
            action_rows=action_rows,
            interpretation=interpretation,
        )


def write_permission_loss_edge_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: PermissionLossEdgeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
