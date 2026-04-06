from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134PCAShareLimitHaltDerivationReviewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.promotion_review_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_daily_market_promotion_review_v1.csv"
        )
        self.limit_halt_candidate_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_extension_candidate_surface_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_limit_halt_derivation_review_status_v1.csv"

    def analyze(self) -> V134PCAShareLimitHaltDerivationReviewAuditV1Report:
        promotion_rows = _read_csv(self.promotion_review_path)
        limit_halt_rows = _read_csv(self.limit_halt_candidate_path)

        promotable_now_count = sum(1 for row in promotion_rows if row["promotion_review_state"] == "promotable_now")
        raw_daily_candidate_cover_count = sum(
            1 for row in limit_halt_rows if row["extension_candidate_state"] == "candidate_cover_available"
        )
        limit_halt_materialized_count = sum(1 for row in promotion_rows if row["limit_halt_materialized"] == "True")
        blocked_no_candidate_count = sum(
            1 for row in promotion_rows if row["promotion_review_state"] == "blocked_no_candidate_cover"
        )
        blocked_by_limit_halt_derivation_count = sum(
            1
            for row in promotion_rows
            if row["promotion_review_state"] == "blocked_by_paired_surface_gap"
            and row["raw_index_candidate_present"] == "True"
            and row["limit_halt_materialized"] == "False"
        )

        rows = [
            {
                "component": "limit_halt_candidate_surface",
                "component_state": "raw_candidate_cover_available",
                "coverage_note": f"raw_daily_candidate_cover_count = {raw_daily_candidate_cover_count}",
            },
            {
                "component": "limit_halt_derivation_state",
                "component_state": "semantic_surface_materialized_for_recheck",
                "coverage_note": f"limit_halt_materialized_count = {limit_halt_materialized_count}",
            },
            {
                "component": "daily_market_promotion_dependency",
                "component_state": "replay_recheck_reopened_with_promotable_subset",
                "coverage_note": f"promotable_now_count = {promotable_now_count}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "promotion_review_row_count": len(promotion_rows),
            "promotable_now_count": promotable_now_count,
            "raw_daily_candidate_cover_count": raw_daily_candidate_cover_count,
            "limit_halt_materialized_count": limit_halt_materialized_count,
            "blocked_by_limit_halt_derivation_count": blocked_by_limit_halt_derivation_count,
            "blocked_no_candidate_count": blocked_no_candidate_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_limit_halt_derivation_review_surface_materialized",
        }
        interpretation = [
            "Replay promotion is no longer blocked by index-daily source absence, and the limit-halt semantic layer is no longer missing.",
            "Controlled semantic materialization has reopened replay promotion review with a promotable subset, while residual no-candidate rows remain explicit.",
        ]
        return V134PCAShareLimitHaltDerivationReviewAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PCAShareLimitHaltDerivationReviewAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pc_a_share_limit_halt_derivation_review_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
