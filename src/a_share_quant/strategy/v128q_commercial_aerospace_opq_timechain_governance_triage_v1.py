from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128QCommercialAerospaceOPQTimechainGovernanceTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "interpretation": self.interpretation,
        }


class V128QCommercialAerospaceOPQTimechainGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128QCommercialAerospaceOPQTimechainGovernanceTriageReport:
        summary = {
            "acceptance_posture": "freeze_v128q_commercial_aerospace_opq_timechain_governance_triage_v1",
            "authoritative_status": "retain_time_chain_triplet_and_preopen_veto_as_governance_layers_without_claiming_economic_improvement_yet",
            "next_direction": "upgrade replay and plots with signal_date_execution_date_preopen_status before any new local alpha tuning",
        }
        retained_rows = [
            {
                "theme": "time_chain_triplet",
                "status": "retain",
                "why": "this directly resolves chart-level ambiguity between signal day and execution day",
            },
            {
                "theme": "preopen_decisive_event_veto",
                "status": "retain_as_governance",
                "why": "economically unchanged in current sample, but legally valuable as a top-down future guardrail",
            },
            {
                "theme": "economic_promotion",
                "status": "blocked",
                "why": "the current registry generates zero veto-trigger buy days, so there is no demonstrated replay improvement yet",
            },
        ]
        interpretation = [
            "V1.28Q freezes the first time-chain governance result for commercial aerospace.",
            "The value here is governance clarity, not a new economic promotion: signal/execution/pre-open visibility should become standard metadata before further local optimization.",
        ]
        return V128QCommercialAerospaceOPQTimechainGovernanceTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128QCommercialAerospaceOPQTimechainGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128QCommercialAerospaceOPQTimechainGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128q_commercial_aerospace_opq_timechain_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
