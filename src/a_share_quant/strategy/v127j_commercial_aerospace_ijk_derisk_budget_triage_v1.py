from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127JCommercialAerospaceIJKDeriskBudgetTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127i_path = repo_root / "reports" / "analysis" / "v127i_commercial_aerospace_symbol_phase_aware_derisk_budget_audit_v1.json"

    def analyze(self) -> V127JCommercialAerospaceIJKDeriskBudgetTriageReport:
        v127i = json.loads(self.v127i_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127j_commercial_aerospace_ijk_derisk_budget_triage_v1",
            "reference_variant": "broad_half_reference",
            "reference_final_equity": v127i["summary"]["reference_final_equity"],
            "reference_max_drawdown": v127i["summary"]["reference_max_drawdown"],
            "authoritative_status": "symbol_phase_aware_derisk_budget_stopline",
            "stop_doing": [
                "do_not_continue_symbol_phase_budget_tuning",
                "do_not_replace_v127e_primary_reference",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "verdict": "stopline",
                "reason": "Lineage-aligned budget variants failed to beat the restored v127e reference and only worsened churn or drawdown.",
            },
            {
                "subagent": "Tesla",
                "verdict": "stopline",
                "reason": "No clean increment remains in symbol/phase-aware budget splitting once the replay lineage is aligned.",
            },
            {
                "subagent": "James",
                "verdict": "stopline",
                "reason": "This is now a solved negative: the budget branch does not improve the frontier and should be closed.",
            },
        ]
        interpretation = [
            "V1.27J freezes the symbol/phase-aware de-risk budget branch as a stopline after replay-lineage alignment.",
            "Commercial aerospace should keep v127e broad-half as the primary reference and stop tuning this budget branch.",
        ]
        return V127JCommercialAerospaceIJKDeriskBudgetTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127JCommercialAerospaceIJKDeriskBudgetTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127j_commercial_aerospace_ijk_derisk_budget_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
