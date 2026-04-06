from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(slots=True)
class V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.eligible_subset_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_execution_eligible_subset_v1.csv"
        )
        self.excluded_boundary_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_execution_eligible_subset_excluded_boundary_v1.csv"
        )
        self.overlay_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_execution_candidate_journal_overlay_v1.csv"
        )
        self.status_csv = (
            repo_root / "data" / "training" / "a_share_shadow_execution_candidate_journal_overlay_status_v1.csv"
        )

    def analyze(self) -> V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Report:
        eligible_rows = _read_csv(self.eligible_subset_path)
        excluded_rows = _read_csv(self.excluded_boundary_path)

        overlay_rows: list[dict[str, Any]] = []
        for row in eligible_rows:
            overlay_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": row["decision_trade_date"],
                    "corrected_query_trade_date": row["corrected_query_trade_date"],
                    "replay_status": row["replay_status"],
                    "visible_event_count": row["visible_event_count"],
                    "visible_high_conf_event_count": row["visible_high_conf_event_count"],
                    "candidate_journal_state": "shadow_execution_candidate_journal_overlay_row",
                    "overlay_scope": "shadow_only",
                }
            )

        _write_csv(self.overlay_path, overlay_rows)

        status_rows = [
            {
                "component": "shadow_execution_candidate_journal_overlay",
                "component_state": "materialized_shadow_only_candidate_journal_overlay",
                "overlay_row_count": len(overlay_rows),
                "excluded_boundary_count": len(excluded_rows),
            },
            {
                "component": "overlay_boundary_policy",
                "component_state": "retain_boundary_rows_outside_candidate_overlay",
                "overlay_row_count": len(overlay_rows),
                "excluded_boundary_count": len(excluded_rows),
            },
        ]
        _write_csv(self.status_csv, status_rows)

        summary = {
            "overlay_row_count": len(overlay_rows),
            "excluded_boundary_count": len(excluded_rows),
            "overlay_path": str(self.overlay_path.relative_to(self.repo_root)),
            "status_csv": str(self.status_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_execution_candidate_journal_overlay_materialized",
        }
        interpretation = [
            "The candidate journal overlay turns the 15-row eligible subset into a concrete shadow-only journal-shaped surface.",
            "That makes replay internal build more operational without pretending the two excluded boundary rows belong inside the same journal lane.",
        ]
        return V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Report(
            summary=summary, rows=status_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qc_a_share_shadow_execution_candidate_journal_overlay_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
