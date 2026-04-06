from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132RCommercialAerospaceQRGovernanceStackTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132RCommercialAerospaceQRGovernanceStackTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stack_report_path = (
            repo_root / "reports" / "analysis" / "v132q_commercial_aerospace_governance_stack_refresh_v2.json"
        )

    def analyze(self) -> V132RCommercialAerospaceQRGovernanceStackTriageReport:
        stack_report = json.loads(self.stack_report_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v132r_commercial_aerospace_qr_governance_stack_triage_v1",
            "authoritative_status": "freeze_commercial_aerospace_governance_stack_v2_with_intraday_layers_and_keep_lawful_eod_primary_unchanged",
            "governance_layer_count": stack_report["summary"]["governance_layer_count"],
            "current_primary_variant": stack_report["summary"]["current_primary_variant"],
            "authoritative_rule": "a stronger intraday supervision branch should widen the governance stack before it is ever allowed to alter the lawful EOD replay",
        }
        triage_rows = [
            {
                "component": "commercial_aerospace_governance_stack_v2",
                "status": "freeze_commercial_aerospace_governance_stack_v2_with_intraday_layers",
                "rationale": "the local minute branch has now earned explicit governance slots through registry, label, and shadow-benefit evidence",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the intraday branch remains governance-first and must not directly rewrite the frozen lawful replay path yet",
            },
        ]
        interpretation = [
            "V1.32R freezes the refreshed governance stack after the local minute branch earned stronger bounded-supervision status.",
            "The decision is organizational, not promotional: the governance stack expands, while the lawful EOD primary stays intact.",
        ]
        return V132RCommercialAerospaceQRGovernanceStackTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132RCommercialAerospaceQRGovernanceStackTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132RCommercialAerospaceQRGovernanceStackTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132r_commercial_aerospace_qr_governance_stack_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
