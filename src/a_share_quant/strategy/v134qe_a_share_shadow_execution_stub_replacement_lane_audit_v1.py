from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qc_a_share_shadow_execution_candidate_journal_overlay_audit_v1 import (
    V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer,
)


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
class V134QEAShareShadowExecutionStubReplacementLaneAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stub_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_execution_journal_stub_v1.csv"
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
            repo_root / "data" / "training" / "a_share_shadow_execution_stub_replacement_lane_status_v1.csv"
        )

    def analyze(self) -> V134QEAShareShadowExecutionStubReplacementLaneAuditV1Report:
        stub_rows = _read_csv(self.stub_path)
        overlay_report = V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer(self.repo_root).analyze()
        overlay_rows = _read_csv(self.overlay_path)

        rows = [
            {
                "component": "base_shadow_execution_stub",
                "component_state": "retained_base_stub_registry",
                "stub_row_count": len(stub_rows),
                "lane_overlay_row_count": len(overlay_rows),
                "excluded_boundary_count": overlay_report.summary["excluded_boundary_count"],
            },
            {
                "component": "shadow_stub_replacement_lane",
                "component_state": "shadow_only_overlay_lane_materialized",
                "stub_row_count": len(stub_rows),
                "lane_overlay_row_count": len(overlay_rows),
                "excluded_boundary_count": overlay_report.summary["excluded_boundary_count"],
            },
            {
                "component": "replacement_boundary",
                "component_state": "do_not_replace_base_stub_globally_while_boundary_rows_stay_excluded",
                "stub_row_count": len(stub_rows),
                "lane_overlay_row_count": len(overlay_rows),
                "excluded_boundary_count": overlay_report.summary["excluded_boundary_count"],
            },
        ]
        _write_csv(self.status_csv, rows)

        summary = {
            "stub_row_count": len(stub_rows),
            "lane_overlay_row_count": len(overlay_rows),
            "excluded_boundary_count": overlay_report.summary["excluded_boundary_count"],
            "status_csv": str(self.status_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_execution_stub_replacement_lane_surface_materialized",
        }
        interpretation = [
            "The shadow execution stub now has an explicit replacement lane instead of a single undifferentiated replacement decision.",
            "That lane covers the 15-row shadow-only candidate journal overlay while the 2 external boundary rows remain outside the replacement scope.",
        ]
        return V134QEAShareShadowExecutionStubReplacementLaneAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QEAShareShadowExecutionStubReplacementLaneAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qe_a_share_shadow_execution_stub_replacement_lane_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
