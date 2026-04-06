from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127TCommercialAerospaceSTUPostPressureDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127TCommercialAerospaceSTUPostPressureDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127s_path = repo_root / "reports" / "analysis" / "v127s_commercial_aerospace_rst_pressure_relocation_triage_v1.json"

    def analyze(self) -> V127TCommercialAerospaceSTUPostPressureDirectionTriageReport:
        v127s = json.loads(self.v127s_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127t_commercial_aerospace_stu_post_pressure_direction_triage_v1",
            "current_primary_variant": v127s["summary"]["reference_variant"],
            "current_primary_final_equity": 1276010.378,
            "current_primary_max_drawdown": 0.11536441,
            "authoritative_next_step": "window_specific_derisk_grammar_for_20260112_to_20260212",
            "stop_doing": [
                "do_not_continue_symbol_pressure_relocation_tuning",
                "do_not_continue_reentry_cooldown_tuning",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "window_specific_derisk_grammar",
                "reason": "The pressure relocation branch is exhausted; the largest remaining increment is in the main drawdown window grammar.",
            },
            {
                "subagent": "Tesla",
                "vote": "window_specific_derisk_grammar",
                "reason": "The post-promotion frontier now hinges on better de-risk behavior in the main 20260112->20260212 window, not more symbol-level tuning.",
            },
            {
                "subagent": "James",
                "vote": "window_specific_derisk_grammar",
                "reason": "The remaining optimization surface is window-level downside control: when to cut, how much to cut, and when to stop cutting.",
            },
        ]
        interpretation = [
            "V1.27T freezes the post-pressure-relocation direction after a unanimous subagent vote.",
            "Commercial aerospace should now move from symbol tuning to window-specific de-risk grammar on the largest drawdown window.",
        ]
        return V127TCommercialAerospaceSTUPostPressureDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127TCommercialAerospaceSTUPostPressureDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127TCommercialAerospaceSTUPostPressureDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127t_commercial_aerospace_stu_post_pressure_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
