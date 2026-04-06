from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128w_commercial_aerospace_phase_state_machine_audit_v1 import (
    V128WCommercialAerospacePhaseStateMachineAuditAnalyzer,
)


@dataclass(slots=True)
class V128XCommercialAerospacePhaseStateMachineTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V128XCommercialAerospacePhaseStateMachineTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128XCommercialAerospacePhaseStateMachineTriageReport:
        audit = V128WCommercialAerospacePhaseStateMachineAuditAnalyzer(self.repo_root).analyze()
        retained_rows = [
            {
                "state": "probe",
                "status": "retain",
                "why": "still the lawful low-intensity starter state",
            },
            {
                "state": "full_pre",
                "status": "retain_for_translation",
                "why": "preheat-window full-quality rows are numerous and nearly identical in quality to later impulse full rows while occurring earlier in chronology",
            },
            {
                "state": "full",
                "status": "retain",
                "why": "impulse-window fully confirmed participation remains the top-intensity state",
            },
            {
                "state": "de_risk",
                "status": "retain",
                "why": "downside grammar still needs de-risk as an explicit state rather than an implicit veto only",
            },
        ]
        blocked_rows = [
            {
                "state": "replay_promotion_now",
                "status": "blocked",
                "why": "state-machine formalization should come before any new replay promotion so that shadow economics are not reinterpreted ad hoc",
            }
        ]
        summary = {
            "acceptance_posture": "freeze_v128x_commercial_aerospace_phase_state_machine_triage_v1",
            "authoritative_status": "retain_probe_full_pre_full_de_risk_state_machine_for_translation",
            "full_pre_count": audit.summary["full_pre_count"],
            "full_count": audit.summary["full_count"],
            "next_direction": "translate the state machine into a lawful supervised table refresh before any new commercial-aerospace replay tuning",
        }
        interpretation = [
            "V1.28X freezes the commercial-aerospace participation state machine after macro-supervision review.",
            "The middle state is no longer optional: full-pre should be treated as a lawful translation target, not as a replay-facing shortcut.",
        ]
        return V128XCommercialAerospacePhaseStateMachineTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128XCommercialAerospacePhaseStateMachineTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128XCommercialAerospacePhaseStateMachineTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128x_commercial_aerospace_phase_state_machine_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
