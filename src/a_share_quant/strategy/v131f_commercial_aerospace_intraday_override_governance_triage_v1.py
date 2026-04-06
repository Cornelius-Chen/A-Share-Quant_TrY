from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131FCommercialAerospaceIntradayOverrideGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131FCommercialAerospaceIntradayOverrideGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervision_report_path = (
            repo_root / "reports" / "analysis" / "v131d_commercial_aerospace_intraday_override_supervision_table_v1.json"
        )
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131e_commercial_aerospace_intraday_override_case_control_audit_v1.json"
        )

    def analyze(self) -> V131FCommercialAerospaceIntradayOverrideGovernanceTriageReport:
        supervision = json.loads(self.supervision_report_path.read_text(encoding="utf-8"))
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))

        open_to_close_separation = float(audit["summary"]["open_to_close_separation"])
        close_location_separation = float(audit["summary"]["close_location_separation"])
        forward_separation = float(audit["summary"]["forward_return_10_separation"])

        retain_for_intraday_seed = (
            supervision["summary"]["override_positive_count"] >= 2
            and open_to_close_separation <= -0.05
            and close_location_separation <= -0.2
            and forward_separation <= -0.1
        )

        triage_rows = [
            {
                "component": "override_positive_seed_set",
                "status": "retain_supervision_seed" if retain_for_intraday_seed else "insufficient",
                "rationale": "severe failures remain materially distinct from clean controls and should be preserved for future minute-level point-in-time labeling",
            },
            {
                "component": "current_eod_primary_replay",
                "status": "do_not_modify",
                "rationale": "execution-day path information keeps the override construct outside lawful EOD replay for now",
            },
            {
                "component": "future_intraday_work",
                "status": "next_priority",
                "rationale": "use retained override positives, reversal watches, and clean controls as the starting supervision geometry once minute-level point-in-time support is available",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v131f_commercial_aerospace_intraday_override_governance_triage_v1",
            "authoritative_status": (
                "retain_intraday_override_supervision_bundle_and_keep_it_outside_current_lawful_replay"
                if retain_for_intraday_seed
                else "retain_watch_only_and_keep_it_outside_current_lawful_replay"
            ),
            "override_positive_count": supervision["summary"]["override_positive_count"],
            "clean_control_count": supervision["summary"]["clean_control_count"],
            "open_to_close_separation": audit["summary"]["open_to_close_separation"],
            "close_location_separation": audit["summary"]["close_location_separation"],
            "forward_return_10_separation": audit["summary"]["forward_return_10_separation"],
            "authoritative_rule": "preserve the intraday override supervision bundle for future minute-level work, but do not retrofit it into the current EOD lawful replay",
        }
        interpretation = [
            "V1.31F freezes the new intraday override bundle as governance-only infrastructure.",
            "It answers a narrow question: is the bundle worth preserving for future point-in-time intraday work even though it must stay outside the current lawful replay stack?",
        ]
        return V131FCommercialAerospaceIntradayOverrideGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131FCommercialAerospaceIntradayOverrideGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131FCommercialAerospaceIntradayOverrideGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131f_commercial_aerospace_intraday_override_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
