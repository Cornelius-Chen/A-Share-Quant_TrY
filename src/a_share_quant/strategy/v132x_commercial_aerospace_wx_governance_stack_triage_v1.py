from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132XCommercialAerospaceWXGovernanceStackTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132XCommercialAerospaceWXGovernanceStackTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stack_v3_path = (
            repo_root / "reports" / "analysis" / "v132w_commercial_aerospace_governance_stack_refresh_v3.json"
        )

    def analyze(self) -> V132XCommercialAerospaceWXGovernanceStackTriageReport:
        stack_v3 = json.loads(self.stack_v3_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v132x_commercial_aerospace_wx_governance_stack_triage_v1",
            "authoritative_status": "freeze_commercial_aerospace_governance_stack_v3_with_state_transition_aligned_minute_branch",
            "governance_layer_count": stack_v3["summary"]["governance_layer_count"],
            "current_primary_variant": stack_v3["summary"]["current_primary_variant"],
            "authoritative_rule": "ordered minute escalation belongs inside the governance stack as a state-machine extension, not as replay execution",
        }
        triage_rows = [
            {
                "component": "commercial_aerospace_governance_stack_v3",
                "status": "freeze_commercial_aerospace_governance_stack_v3_with_state_transition_aligned_minute_branch",
                "rationale": "the minute branch now has registry, rule, shadow-benefit, action-ladder, and state-transition support",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the intraday branch continues to strengthen governance and future design, but still does not alter the frozen EOD replay",
            },
        ]
        interpretation = [
            "V1.32X freezes governance stack v3 after the local minute branch proved ordered escalation on broader hit sessions.",
            "This is the stronger governance endpoint of the current commercial-aerospace minute work, not a replay-side promotion.",
        ]
        return V132XCommercialAerospaceWXGovernanceStackTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132XCommercialAerospaceWXGovernanceStackTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132XCommercialAerospaceWXGovernanceStackTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132x_commercial_aerospace_wx_governance_stack_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
