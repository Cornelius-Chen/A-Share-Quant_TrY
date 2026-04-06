from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bu_holdings_binding_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "phase2_wider_reference_mapping",
                "status": "not_execution_bindable_as_is",
                "detail": "Do not treat the current wider sell shadow as if its reference quantities were real holdings; most sessions are only partially funded or unfunded relative to the frozen EOD primary.",
            },
            {
                "component": "next_real_work",
                "status": "build_start_of_day_holdings_ledger",
                "detail": "The next justified step is a holdings-aware ledger that converts frozen EOD positions into sellable start-of-day intraday state.",
            },
            {
                "component": "same_day_precedence_policy",
                "status": "mandatory",
                "detail": "A same-day precedence rule is required because some sell-side candidates collide with same-day primary open/add/reduce actions.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep this step sell-side only; do not pull reentry execution or full replay binding into the holdings-aware buildout.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bv_commercial_aerospace_bu_holdings_binding_direction_triage_v1",
            "authoritative_status": "freeze_holdings_mapping_gap_and_build_start_of_day_sell_binding_surface_next",
            "broader_hit_session_count": audit["summary"]["broader_hit_session_count"],
            "fully_funded_overlap_count": audit["summary"]["fully_funded_overlap_count"],
            "same_day_primary_collision_count": audit["summary"]["same_day_primary_collision_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BV converts the holdings-aware audit into a practical direction judgment.",
            "The branch should next build a start-of-day holdings-aware sell surface plus same-day precedence policy, not pretend the current wider shadow can bind directly into the frozen EOD primary.",
        ]
        return V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bv_commercial_aerospace_bu_holdings_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
