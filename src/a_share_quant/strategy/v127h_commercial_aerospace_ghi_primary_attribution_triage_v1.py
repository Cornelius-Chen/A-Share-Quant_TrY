from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127HCommercialAerospaceGHIPrimaryAttributionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127HCommercialAerospaceGHIPrimaryAttributionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127g_path = repo_root / "reports" / "analysis" / "v127g_commercial_aerospace_primary_reference_attribution_v1.json"

    def analyze(self) -> V127HCommercialAerospaceGHIPrimaryAttributionTriageReport:
        v127g = json.loads(self.v127g_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127h_commercial_aerospace_ghi_primary_attribution_triage_v1",
            "primary_variant": v127g["summary"]["primary_variant"],
            "primary_final_equity": v127g["summary"]["primary_final_equity"],
            "primary_max_drawdown": v127g["summary"]["primary_max_drawdown"],
            "authoritative_next_step": "symbol_phase_aware_derisk_budget",
            "stop_doing": [
                "do_not_open_another_downside_family_yet",
                "do_not_shift_attention_to_aggressive_shadow_first",
                "do_not_continue_same_family_grammar_micro_tuning",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "symbol_phase_aware_derisk_budget",
                "reason": "v127e already de-risks more in the main drawdown window, so the next bottleneck is budget allocation by symbol and phase rather than willingness to sell.",
            },
            {
                "subagent": "Tesla",
                "vote": "symbol_phase_aware_derisk_budget",
                "reason": "The replay frontier is already improved; the next increment should come from better budget efficiency, not another downside grammar search.",
            },
            {
                "subagent": "James",
                "vote": "symbol_phase_aware_derisk_budget",
                "reason": "Window-level drawdown did not compress despite much larger reduce notional, so de-risk budget placement is now the right control problem.",
            },
        ]
        interpretation = [
            "V1.27H freezes the next-step direction after attribution: the new primary reference is good enough to stop discovery and start budget allocation work.",
            "Commercial aerospace should now optimize how much to de-risk by symbol and phase, not whether to search another downside family.",
        ]
        return V127HCommercialAerospaceGHIPrimaryAttributionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127HCommercialAerospaceGHIPrimaryAttributionTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127HCommercialAerospaceGHIPrimaryAttributionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127h_commercial_aerospace_ghi_primary_attribution_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
