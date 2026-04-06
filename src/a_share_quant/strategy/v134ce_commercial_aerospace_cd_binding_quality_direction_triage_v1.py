from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cd_binding_quality_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        triage_rows = [
            {
                "component": "isolated_sell_side_binding_surface",
                "status": "retain_as_first_real_binding_reference",
                "detail": (
                    f"executed_session_count = {summary['executed_session_count']}, "
                    f"total_protected_mark_to_close = {summary['total_protected_mark_to_close']}"
                ),
            },
            {
                "component": "same_day_new_lots_protection",
                "status": "verified",
                "detail": (
                    f"same_day_new_lots_protected_total = {summary['same_day_new_lots_protected_total']}, "
                    f"no_inventory_same_day_new_lots_only_count = {summary['no_inventory_same_day_new_lots_only_count']}"
                ),
            },
            {
                "component": "reconciliation_clipping",
                "status": "retain_and_explicitly_preserve",
                "detail": (
                    f"clipped_reconciliation_count = {summary['clipped_reconciliation_count']}, "
                    f"clipped_quantity_total = {summary['clipped_quantity_total']}"
                ),
            },
            {
                "component": "next_real_work",
                "status": "do_not_expand_surface_build_horizon_quality_next",
                "detail": "The next justified work is horizon and attribution quality on the isolated binding lane, not replay binding or wider surface expansion.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep the branch sell-side only, holdings-aware only, and continue excluding reentry execution plus full replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1",
            "authoritative_status": "retain_isolated_sell_side_binding_surface_and_audit_horizon_quality_next",
            "executed_session_count": summary["executed_session_count"],
            "total_protected_mark_to_close": summary["total_protected_mark_to_close"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CE turns the first binding-quality audit into the next direction judgment.",
            "The isolated sell-side lane should now be treated as the first real holdings-aware binding reference, but the next step is horizon-quality audit rather than replay expansion.",
        ]
        return V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
