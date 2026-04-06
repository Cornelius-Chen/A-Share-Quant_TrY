from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128KCommercialAerospacePortabilityPackagingReport:
    summary: dict[str, Any]
    portable_rows: list[dict[str, Any]]
    local_only_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "portable_rows": self.portable_rows,
            "local_only_rows": self.local_only_rows,
            "interpretation": self.interpretation,
        }


class V128KCommercialAerospacePortabilityPackagingAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_path = repo_root / "reports" / "analysis" / "v128i_commercial_aerospace_hij_tail_repair_promotion_triage_v1.json"
        self.grammar_path = repo_root / "reports" / "analysis" / "v128b_commercial_aerospace_current_primary_execution_grammar_v1.json"
        self.portability_path = repo_root / "reports" / "analysis" / "v128c_commercial_aerospace_current_primary_portability_audit_v1.json"

    def analyze(self) -> V128KCommercialAerospacePortabilityPackagingReport:
        primary = json.loads(self.primary_path.read_text(encoding="utf-8"))
        grammar = json.loads(self.grammar_path.read_text(encoding="utf-8"))
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))

        portable_rows = [
            {
                "layer": "research_discipline",
                "rule": "lawful_eod_supervised_plus_tplus1_replay_only",
                "why_portable": "This is methodology, not board-specific semantics.",
            },
            {
                "layer": "entry_architecture",
                "rule": "entry_surface_stable_then_fix_downside_before_reopening_aggression",
                "why_portable": "The winning path came from preserving entry and improving downside execution rather than endlessly heating entry.",
            },
            {
                "layer": "main_window_downside",
                "rule": "inside the dominant drawdown window, deepen impulse-target de-risk before touching broader entry or symbol tuning",
                "why_portable": "This is a grammar about repairing the largest economic leak first.",
            },
            {
                "layer": "tail_repair",
                "rule": "after main-window repair, check post-window weak-drift tail giveback before more local alpha discovery",
                "why_portable": "The sequence main-window then tail was economically justified by the portability audit.",
            },
            {
                "layer": "promotion_rule",
                "rule": "only promote when higher equity, lower-or-equal drawdown, and lower-or-equal order count all improve together",
                "why_portable": "This is the same frontier discipline that prevented false promotions in CPO and sharpened commercial-aerospace promotion quality.",
            },
        ]

        local_only_rows = [
            {
                "layer": "theme_archetype",
                "rule": "commercial_aerospace_is_catalyst_concentrated_sentiment_amplified_thematic_impulse",
                "why_local_only": "This board archetype must not be mixed with CPO-style sustained diffusion boards.",
            },
            {
                "layer": "window_definition",
                "rule": "main_window_20260112_to_20260212 and post_window_after_20260212",
                "why_local_only": "The exact chronology windows are commercial-aerospace specific.",
            },
            {
                "layer": "current_primary_name",
                "rule": primary["summary"]["new_primary_variant"],
                "why_local_only": "The named rule is specific to this board's regime semantics and replay path.",
            },
            {
                "layer": "symbol_pressure_map",
                "rule": "688568/600118/600879 help; 300342/000738/601698 carry pressure",
                "why_local_only": "These are board-specific symbol findings and should not be ported as generic priors.",
            },
            {
                "layer": "portability_limit",
                "rule": portability["summary"]["portability_status"],
                "why_local_only": "The current grammar is portable enough to package, but its measured concentration is still a board-specific audit result.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v128k_commercial_aerospace_portability_packaging_v1",
            "current_primary_variant": primary["summary"]["new_primary_variant"],
            "current_primary_final_equity": primary["summary"]["new_primary_final_equity"],
            "current_primary_max_drawdown": primary["summary"]["new_primary_max_drawdown"],
            "execution_grammar_compaction": grammar["summary"]["execution_grammar_compaction"],
            "portability_status": portability["summary"]["portability_status"],
            "authoritative_output": "commercial_aerospace_primary_is_packaged_for_cross_board_transfer_without_mixing_archetypes",
        }
        interpretation = [
            "V1.28K packages the commercial-aerospace primary into portable methodology versus local-only board semantics.",
            "This is not a migration itself; it is the guardrail that prevents future cross-board transfer from mixing transferable grammar with commercial-aerospace-specific chronology and symbol facts.",
        ]
        return V128KCommercialAerospacePortabilityPackagingReport(
            summary=summary,
            portable_rows=portable_rows,
            local_only_rows=local_only_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128KCommercialAerospacePortabilityPackagingReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128KCommercialAerospacePortabilityPackagingAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128k_commercial_aerospace_portability_packaging_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
