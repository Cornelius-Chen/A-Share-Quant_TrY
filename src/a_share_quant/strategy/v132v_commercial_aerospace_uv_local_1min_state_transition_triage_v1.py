from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132VCommercialAerospaceUVLocal1MinStateTransitionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132VCommercialAerospaceUVLocal1MinStateTransitionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132u_commercial_aerospace_local_1min_state_transition_audit_v1.json"
        )

    def analyze(self) -> V132VCommercialAerospaceUVLocal1MinStateTransitionTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]
        authoritative_status = (
            "retain_local_1min_branch_as_state_transition_aligned_governance"
            if summary["severe_hits_with_prior_reversal_share"] >= 0.5
            else "retain_local_1min_branch_as_shadow_benefit_governance_without_state_transition_upgrade"
        )
        triage_rows = [
            {
                "component": "local_1min_state_transition_audit",
                "status": authoritative_status,
                "rationale": "ordered intraday escalation strengthens the case that the minute branch is a real governance state machine rather than only a static label screen",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "better state-transition semantics still do not authorize direct replay modification",
            },
        ]
        triage_summary = {
            "acceptance_posture": "freeze_v132v_commercial_aerospace_uv_local_1min_state_transition_triage_v1",
            "authoritative_status": authoritative_status,
            "severe_hits_with_prior_reversal_share": summary["severe_hits_with_prior_reversal_share"],
            "top_transition_pattern": summary["top_transition_pattern"],
            "authoritative_rule": "the local 1min branch becomes stronger governance when hit sessions exhibit ordered intraday escalation patterns that match the proposed action ladder",
        }
        interpretation = [
            "V1.32V converts the intraday state-transition audit into a governance verdict.",
            "The branch remains governance-first; the question is whether it should now be treated as an actual escalation ladder inside the commercial-aerospace state machine.",
        ]
        return V132VCommercialAerospaceUVLocal1MinStateTransitionTriageReport(
            summary=triage_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132VCommercialAerospaceUVLocal1MinStateTransitionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132VCommercialAerospaceUVLocal1MinStateTransitionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132v_commercial_aerospace_uv_local_1min_state_transition_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
