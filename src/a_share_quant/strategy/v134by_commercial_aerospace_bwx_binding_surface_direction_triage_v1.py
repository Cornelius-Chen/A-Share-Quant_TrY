from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.surface_spec_path = (
            repo_root / "reports" / "analysis" / "v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1.json"
        )
        self.precedence_path = (
            repo_root / "reports" / "analysis" / "v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bwx_binding_surface_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Report:
        surface_spec = json.loads(self.surface_spec_path.read_text(encoding="utf-8"))
        precedence = json.loads(self.precedence_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "start_of_day_holdings_ledger",
                "status": "approved_for_build",
                "detail": "Build a carried-inventory ledger first; the current wider sell shadow cannot bind without it.",
            },
            {
                "component": "same_day_precedence_policy",
                "status": "approved_for_build",
                "detail": "Build explicit precedence for open/add protection and EOD reduce/close reconciliation before opening an isolated sell-side lane.",
            },
            {
                "component": "isolated_sell_side_shadow_lane",
                "status": "blocked_until_surface_exists",
                "detail": "Do not open the isolated lane before the ledger and precedence policy exist as concrete surfaces.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep the next step sell-side only and continue excluding reentry execution and full replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134by_commercial_aerospace_bwx_binding_surface_direction_triage_v1",
            "authoritative_status": "freeze_binding_surface_spec_and_build_ledger_plus_precedence_before_isolated_lane",
            "must_build_component_count": surface_spec["summary"]["must_build_component_count"],
            "collision_session_count": precedence["summary"]["collision_session_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BY converts the holdings-ledger and precedence audits into the next binding direction.",
            "The branch should build the ledger and precedence surfaces first, then revisit whether an isolated sell-side shadow lane is safe to open.",
        ]
        return V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134by_commercial_aerospace_bwx_binding_surface_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
