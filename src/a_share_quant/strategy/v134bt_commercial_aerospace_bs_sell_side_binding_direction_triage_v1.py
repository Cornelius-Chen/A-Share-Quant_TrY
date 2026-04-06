from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bs_sell_side_binding_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "sell_side_visibility",
                "status": "good_enough_shadow_input",
                "detail": "Do not reopen visibility research; phase-1 all-session visibility is already sufficient as the sell-side input surface.",
            },
            {
                "component": "sell_side_simulator_logic",
                "status": "good_enough_shadow_reference",
                "detail": "Do not reopen same-family sell logic search; current broader-hit sell shadow is sufficient as a binding reference.",
            },
            {
                "component": "next_real_work",
                "status": "build_missing_binding_surfaces_only",
                "detail": "The only justified next work is holdings-aware sell binding and an isolated sell-side shadow lane.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Do not pull board reentry execution or full replay lane into this next step; keep it sell-side only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bt_commercial_aerospace_bs_sell_side_binding_direction_triage_v1",
            "authoritative_status": "freeze_sell_side_binding_readiness_and_build_only_missing_binding_surfaces",
            "ready_shadow_input_count": audit["summary"]["ready_shadow_input_count"],
            "missing_binding_component_count": audit["summary"]["missing_binding_component_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BT converts the readiness audit into a practical direction judgment.",
            "The branch should stop researching sell-side semantics and instead build the two missing binding surfaces without dragging replay or reentry into scope.",
        ]
        return V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BTCommercialAerospaceBSSellSideBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bt_commercial_aerospace_bs_sell_side_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
