from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132ZCommercialAerospaceYZIntradayCasePanelTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132ZCommercialAerospaceYZIntradayCasePanelTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.panel_report_path = (
            repo_root / "reports" / "analysis" / "v132y_commercial_aerospace_intraday_seed_case_panel_v1.json"
        )

    def analyze(self) -> V132ZCommercialAerospaceYZIntradayCasePanelTriageReport:
        panel_report = json.loads(self.panel_report_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v132z_commercial_aerospace_yz_intraday_case_panel_triage_v1",
            "authoritative_status": "retain_intraday_seed_case_panel_as_governance_visual_reference",
            "seed_case_count": panel_report["summary"]["seed_case_count"],
            "authoritative_rule": "the commercial-aerospace minute branch should preserve a canonical visual case panel so future lawful intraday work can be anchored to inspectable sessions rather than only abstract rules",
        }
        triage_rows = [
            {
                "component": "intraday_seed_case_panel",
                "status": "retain_intraday_seed_case_panel_as_governance_visual_reference",
                "rationale": "the governance stack is stronger when its minute tiers and escalation rules remain tied to explicit inspectable sessions",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the case panel improves supervision transparency without changing the frozen replay path",
            },
        ]
        interpretation = [
            "V1.32Z freezes the intraday seed case panel as the visual reference layer for the commercial-aerospace minute branch.",
            "The panel is governance infrastructure, not replay promotion.",
        ]
        return V132ZCommercialAerospaceYZIntradayCasePanelTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132ZCommercialAerospaceYZIntradayCasePanelTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132ZCommercialAerospaceYZIntradayCasePanelTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132z_commercial_aerospace_yz_intraday_case_panel_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
