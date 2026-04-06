from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ne_a_share_index_daily_source_horizon_gap_audit_v1 import (
    V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_index_daily_source_extension_opening_checklist_v1.csv"
        )

    def analyze(self) -> V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Report:
        report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(self.repo_root).analyze()
        source_present = report.summary["beyond_2024_source_count"] > 0
        horizon_covers = bool(report.summary["max_raw_coverage_end"]) and report.summary["max_raw_coverage_end"] >= report.summary["shadow_horizon_end"]
        checklist_rows = [
            {
                "opening_gate": "new_raw_index_source_present",
                "gate_state": "open" if source_present else "closed",
                "gate_reason": (
                    "retained raw index source now extends beyond 2024-12-31"
                    if source_present
                    else "no retained raw index source extends beyond 2024-12-31"
                ),
            },
            {
                "opening_gate": "new_raw_source_horizon_covers_shadow_window",
                "gate_state": "open" if horizon_covers else "closed",
                "gate_reason": (
                    f"retained index source horizon now reaches shadow_horizon_end = {report.summary['shadow_horizon_end']}"
                    if horizon_covers
                    else f"shadow_horizon_end = {report.summary['shadow_horizon_end']} remains beyond retained index source horizon"
                ),
            },
            {
                "opening_gate": "index_daily_registry_materialization_reviewable",
                "gate_state": "open" if source_present else "closed",
                "gate_reason": (
                    "materialization review may reopen because new raw source is now present"
                    if source_present
                    else "materialization review should not reopen until new raw source exists"
                ),
            },
            {
                "opening_gate": "paired_surface_promotion_recheck",
                "gate_state": "open" if source_present else "closed",
                "gate_reason": (
                    "paired surface promotion may now be rechecked because index-daily source boundary moved"
                    if source_present
                    else "paired surface promotion must remain blocked until index-daily source boundary moves"
                ),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "opening_gate_count": len(checklist_rows),
            "closed_gate_count": sum(row["gate_state"] == "closed" for row in checklist_rows),
            "ready_to_open_now": source_present and horizon_covers,
            "silent_opening_allowed": False,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_index_daily_source_extension_checklist_materialized",
        }
        interpretation = [
            "Index-daily extension remains an explicit opening process rather than a silent retry path.",
            (
                "The opening conditions are now materially satisfied by new raw source arrival, so downstream re-audit can begin."
                if source_present
                else "The first real opening condition is new raw index source availability; everything else remains downstream of that."
            ),
        ]
        return V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Report(
            summary=summary, checklist_rows=checklist_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oa_a_share_index_daily_source_extension_opening_checklist_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
