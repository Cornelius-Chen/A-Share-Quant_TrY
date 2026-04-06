from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cf_horizon_quality_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        triage_rows = [
            {
                "component": "same_day_protection",
                "status": "retain",
                "detail": f"same_day_protected_mark_to_close_total = {summary['same_day_protected_mark_to_close_total']}",
            },
            {
                "component": "short_horizon_followthrough",
                "status": "retain_with_horizon_caveat",
                "detail": (
                    f"net_horizon_pnl_if_held_1d = {summary['net_horizon_pnl_if_held_1d']}, "
                    f"net_horizon_pnl_if_held_3d = {summary['net_horizon_pnl_if_held_3d']}, "
                    f"net_horizon_pnl_if_held_5d = {summary['net_horizon_pnl_if_held_5d']}"
                ),
            },
            {
                "component": "next_real_work",
                "status": "do_not_expand_surface_local_binding_attribution_next",
                "detail": "The next justified work is local attribution/failure review inside the isolated sell-side lane, not replay binding or reentry execution.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep the branch sell-side only and holdings-aware only; do not reopen wider all-session expansion or full replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1",
            "authoritative_status": "retain_isolated_sell_side_binding_surface_with_horizon_caveat_and_audit_local_binding_attribution_next",
            "executed_order_count": summary["executed_order_count"],
            "same_day_protected_mark_to_close_total": summary["same_day_protected_mark_to_close_total"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CG converts the first horizon audit on the isolated sell-side binding surface into a direction judgment.",
            "The lane remains worth retaining, but now with an explicit horizon caveat and a narrower next step inside local binding attribution rather than replay expansion.",
        ]
        return V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
