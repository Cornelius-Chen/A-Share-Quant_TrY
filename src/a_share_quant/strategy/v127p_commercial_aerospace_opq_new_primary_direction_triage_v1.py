from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127PCommercialAerospaceOPQNewPrimaryDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127PCommercialAerospaceOPQNewPrimaryDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127o_path = repo_root / "reports" / "analysis" / "v127o_commercial_aerospace_new_primary_attribution_v1.json"

    def analyze(self) -> V127PCommercialAerospaceOPQNewPrimaryDirectionTriageReport:
        v127o = json.loads(self.v127o_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127p_commercial_aerospace_opq_new_primary_direction_triage_v1",
            "new_primary_variant": v127o["summary"]["new_primary_variant"],
            "new_primary_final_equity": v127o["summary"]["new_primary_final_equity"],
            "new_primary_max_drawdown": v127o["summary"]["new_primary_max_drawdown"],
            "authoritative_next_step": "new_primary_drawdown_window_attribution",
            "stop_doing": [
                "do_not_continue_selective_symbol_veto_yet",
                "do_not_jump_to_entry_budget_yet",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "new_primary_drawdown_window_attribution",
                "reason": "The selective veto rearranged the burden map, so the next step is to localize exactly which drawdown windows improved and which symbols became the new pressure points.",
            },
            {
                "subagent": "Tesla",
                "vote": "new_primary_drawdown_window_attribution",
                "reason": "Before opening another branch, the replay should explain whether the new frontier gain is robust across windows or just transfers pain from one symbol set to another.",
            },
            {
                "subagent": "James",
                "vote": "new_primary_drawdown_window_attribution",
                "reason": "Window-level attribution is now the highest-value cut because symbol-level totals already show a burden transfer from the old drag trio to 601698 and 000738.",
            },
        ]
        interpretation = [
            "V1.27P freezes the unanimous subagent direction after the new primary promotion.",
            "Commercial aerospace should now study new-primary drawdown windows before opening another symbol-veto or entry-budget branch.",
        ]
        return V127PCommercialAerospaceOPQNewPrimaryDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127PCommercialAerospaceOPQNewPrimaryDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127PCommercialAerospaceOPQNewPrimaryDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127p_commercial_aerospace_opq_new_primary_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
