from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132o_commercial_aerospace_local_1min_shadow_benefit_audit_v1.json"
        )

    def analyze(self) -> V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        retain = (
            summary["flagged_execution_share"] <= 0.15
            and summary["flagged_negative_forward_notional_share"] >= 0.25
            and summary["flagged_adverse_notional_share"] >= 0.25
        )
        authoritative_status = (
            "retain_local_1min_rules_as_shadow_benefit_aligned_window_governance"
            if retain
            else "retain_local_1min_rules_as_supervision_only_without_shadow_benefit_upgrade"
        )
        triage_rows = [
            {
                "component": "local_1min_shadow_benefit_audit",
                "status": authoritative_status,
                "rationale": "the minute branch deserves a stronger governance posture when a narrow flagged slice captures disproportionate later downside notional on the buy surface",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "even aligned shadow-benefit evidence remains outside direct replay execution unless a lawful intraday path is built",
            },
        ]
        triage_summary = {
            "acceptance_posture": "freeze_v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1",
            "authoritative_status": authoritative_status,
            "flagged_execution_share": summary["flagged_execution_share"],
            "flagged_negative_forward_notional_share": summary["flagged_negative_forward_notional_share"],
            "flagged_adverse_notional_share": summary["flagged_adverse_notional_share"],
            "authoritative_rule": "the local 1min branch becomes stronger governance when it stays narrow on executions yet concentrates a disproportionate share of later downside notional",
        }
        interpretation = [
            "V1.32P converts the shadow-benefit audit into a governance verdict.",
            "The intent is still bounded supervision: stronger minute credibility should not be confused with permission to alter the lawful EOD replay directly.",
        ]
        return V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageReport(
            summary=triage_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
