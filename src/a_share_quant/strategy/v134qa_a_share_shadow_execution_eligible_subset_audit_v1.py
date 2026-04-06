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
class V134QAAShareShadowExecutionEligibleSubsetAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.corrected_binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_corrected_tradeable_context_binding_v1.csv"
        )
        self.shadow_surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "replay"
            / "shadow"
            / "a_share_shadow_replay_surface_v1.csv"
        )
        self.stub_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_execution_journal_stub_v1.csv"
        )
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
        self.status_csv = (
            repo_root / "data" / "training" / "a_share_shadow_execution_eligible_subset_status_v1.csv"
        )

    def analyze(self) -> V134QAAShareShadowExecutionEligibleSubsetAuditV1Report:
        corrected_rows = {row["slice_id"]: row for row in _read_csv(self.corrected_binding_path)}
        shadow_rows = {row["slice_id"]: row for row in _read_csv(self.shadow_surface_path)}
        stub_rows = _read_csv(self.stub_path)

        eligible_subset_rows: list[dict[str, Any]] = []
        excluded_boundary_rows: list[dict[str, Any]] = []
        for row in stub_rows:
            corrected_row = corrected_rows[row["slice_id"]]
            shadow_row = shadow_rows[row["slice_id"]]
            if corrected_row["corrected_tradeable_context_state"].startswith("date_level_tradeable_context_bound"):
                eligible_subset_rows.append(
                    {
                        "slice_id": row["slice_id"],
                        "decision_trade_date": row["decision_trade_date"],
                        "corrected_query_trade_date": corrected_row["corrected_query_trade_date"],
                        "replay_status": shadow_row["replay_status"],
                        "visible_event_count": shadow_row["visible_event_count"],
                        "visible_high_conf_event_count": shadow_row["visible_high_conf_event_count"],
                        "execution_journal_state": row["execution_journal_state"],
                        "eligible_subset_state": "shadow_execution_candidate_subset_row",
                    }
                )
            else:
                excluded_boundary_rows.append(
                    {
                        "slice_id": row["slice_id"],
                        "decision_trade_date": row["decision_trade_date"],
                        "corrected_query_trade_date": corrected_row["corrected_query_trade_date"],
                        "baseline_tradeable_context_state": corrected_row["baseline_tradeable_context_state"],
                        "corrected_tradeable_context_state": corrected_row["corrected_tradeable_context_state"],
                        "boundary_exclusion_reason": "external_boundary_residual_outside_current_market_context_window",
                    }
                )

        _write_csv(self.eligible_subset_path, eligible_subset_rows)
        _write_csv(self.excluded_boundary_path, excluded_boundary_rows)

        status_rows = [
            {
                "component": "shadow_execution_eligible_subset",
                "component_state": "materialized_shadow_only_eligible_subset",
                "eligible_subset_count": len(eligible_subset_rows),
                "excluded_boundary_count": len(excluded_boundary_rows),
            },
            {
                "component": "boundary_exclusion_policy",
                "component_state": "exclude_external_boundary_residuals_from_shadow_execution_candidate_subset",
                "eligible_subset_count": len(eligible_subset_rows),
                "excluded_boundary_count": len(excluded_boundary_rows),
            },
        ]
        _write_csv(self.status_csv, status_rows)

        summary = {
            "total_stub_row_count": len(stub_rows),
            "eligible_subset_count": len(eligible_subset_rows),
            "excluded_boundary_count": len(excluded_boundary_rows),
            "eligible_subset_path": str(self.eligible_subset_path.relative_to(self.repo_root)),
            "excluded_boundary_path": str(self.excluded_boundary_path.relative_to(self.repo_root)),
            "status_csv": str(self.status_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_execution_eligible_subset_materialized",
        }
        interpretation = [
            "The shadow-only corrected binding view is now strong enough to support an eligible execution subset without touching the base execution stub.",
            "That leaves the two external boundary residuals explicitly excluded rather than letting them keep the full 17-row stub frozen as one undifferentiated unit.",
        ]
        return V134QAAShareShadowExecutionEligibleSubsetAuditV1Report(
            summary=summary, rows=status_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QAAShareShadowExecutionEligibleSubsetAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qa_a_share_shadow_execution_eligible_subset_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
