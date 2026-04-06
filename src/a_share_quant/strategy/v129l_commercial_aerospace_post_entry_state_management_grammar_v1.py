from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129LCommercialAerospacePostEntryStateManagementGrammarReport:
    summary: dict[str, Any]
    grammar_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "grammar_rows": self.grammar_rows,
            "interpretation": self.interpretation,
        }


class V129LCommercialAerospacePostEntryStateManagementGrammarAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_grammar_path = repo_root / "reports" / "analysis" / "v128b_commercial_aerospace_current_primary_execution_grammar_v1.json"
        self.portability_path = repo_root / "reports" / "analysis" / "v128k_commercial_aerospace_portability_packaging_v1.json"
        self.state_machine_path = repo_root / "reports" / "analysis" / "v128x_commercial_aerospace_phase_state_machine_triage_v1.json"
        self.walk_forward_path = repo_root / "reports" / "analysis" / "v129f_commercial_aerospace_def_walk_forward_direction_triage_v1.json"
        self.late_preheat_path = repo_root / "reports" / "analysis" / "v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1.json"

    def analyze(self) -> V129LCommercialAerospacePostEntryStateManagementGrammarReport:
        primary_grammar = json.loads(self.primary_grammar_path.read_text(encoding="utf-8"))
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))
        state_machine = json.loads(self.state_machine_path.read_text(encoding="utf-8"))
        walk_forward = json.loads(self.walk_forward_path.read_text(encoding="utf-8"))
        late_preheat = json.loads(self.late_preheat_path.read_text(encoding="utf-8"))

        grammar_rows = [
            {
                "step": 1,
                "state_transition": "probe_to_full_pre",
                "rule": "preheat escalation should be acknowledged as a distinct state transition, but replay should not automatically upgrade all late-preheat full adds until the full_pre supervision layer proves economic benefit",
                "source": state_machine["summary"]["authoritative_status"],
            },
            {
                "step": 2,
                "state_transition": "full_pre_to_full",
                "rule": "full remains phase-contextual rather than directly supervised; transition into full must stay tied to impulse window semantics, not generic classifier confidence",
                "source": walk_forward["summary"]["authoritative_status"],
            },
            {
                "step": 3,
                "state_transition": "full_to_main_window_derisk",
                "rule": "the primary commercial-aerospace edge comes from intensifying downside control inside the dominant drawdown window rather than broadening entry heat",
                "source": primary_grammar["summary"]["execution_grammar_compaction"],
            },
            {
                "step": 4,
                "state_transition": "main_window_derisk_to_tail_repair",
                "rule": "after the main drawdown window is repaired, post-window weak-drift selling becomes the next lawful state-management layer",
                "source": portability["summary"]["execution_grammar_compaction"],
            },
            {
                "step": 5,
                "state_transition": "late_preheat_full_mismatch_to_governance",
                "rule": "late-preheat full entries that mismatch the full_pre state must be downgraded into governance/failure review rather than replay-facing promotion candidates",
                "source": late_preheat["summary"]["authoritative_status"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129l_commercial_aerospace_post_entry_state_management_grammar_v1",
            "current_primary_variant": "tail_weakdrift_full",
            "state_management_focus": "post_entry_upgrade_derisk_tail_repair_governance",
            "authoritative_output": "commercial_aerospace_post_entry_state_management_grammar_frozen",
        }
        interpretation = [
            "V1.29L compacts commercial-aerospace into a post-entry state-management grammar rather than another replay frontier table.",
            "The goal is to make the frozen primary reusable: entry remains stable, while upgrades, de-risk, tail repair, and governance are expressed as ordered state transitions.",
        ]
        return V129LCommercialAerospacePostEntryStateManagementGrammarReport(
            summary=summary,
            grammar_rows=grammar_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129LCommercialAerospacePostEntryStateManagementGrammarReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129LCommercialAerospacePostEntryStateManagementGrammarAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129l_commercial_aerospace_post_entry_state_management_grammar_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
