from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134POAShareReplayMarketContextResidualFixabilityAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_replay_market_context_residual_fixability_status_v1.csv"
        )

    def analyze(self) -> V134POAShareReplayMarketContextResidualFixabilityAuditV1Report:
        report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()

        rows: list[dict[str, Any]] = []
        external_boundary_count = 0
        internal_calendar_alignment_count = 0
        for row in report.rows:
            residual_class = row["residual_class"]
            if residual_class == "pre_coverage_shadow_slice":
                fixability_class = "external_boundary_residual"
                suggested_mode = "retain_as_boundary_history_outside_current_market_context_window"
                external_boundary_count += 1
            elif residual_class == "off_calendar_shadow_slice":
                fixability_class = "internal_calendar_alignment_candidate"
                suggested_mode = "inspect_shadow_calendar_alignment_before_treating_as_hard_market_context_gap"
                internal_calendar_alignment_count += 1
            else:
                fixability_class = "unknown_residual"
                suggested_mode = "retain_explicit_until_classified"
            rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": row["decision_trade_date"],
                    "residual_class": residual_class,
                    "fixability_class": fixability_class,
                    "suggested_mode": suggested_mode,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "residual_count": len(rows),
            "external_boundary_count": external_boundary_count,
            "internal_calendar_alignment_count": internal_calendar_alignment_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_market_context_residual_fixability_surface_materialized",
        }
        interpretation = [
            "Replay market-context residuals are no longer just classified by shape; they are now split by likely fixability.",
            "Pre-coverage slices look like external boundary residuals, while the off-calendar slice is a plausible internal calendar-alignment candidate.",
            "That gives the replay lane one small internal improvement target without pretending the whole residual set is internally solvable.",
        ]
        return V134POAShareReplayMarketContextResidualFixabilityAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134POAShareReplayMarketContextResidualFixabilityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134po_a_share_replay_market_context_residual_fixability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
