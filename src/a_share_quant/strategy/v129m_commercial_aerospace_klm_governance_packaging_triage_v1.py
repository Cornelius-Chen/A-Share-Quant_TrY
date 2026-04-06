from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129MCommercialAerospaceKLMGovernancePackagingTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129MCommercialAerospaceKLMGovernancePackagingTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.governance_path = repo_root / "reports" / "analysis" / "v129k_commercial_aerospace_governance_stack_packaging_v1.json"
        self.state_management_path = repo_root / "reports" / "analysis" / "v129l_commercial_aerospace_post_entry_state_management_grammar_v1.json"

    def analyze(self) -> V129MCommercialAerospaceKLMGovernancePackagingTriageReport:
        governance = json.loads(self.governance_path.read_text(encoding="utf-8"))
        state_management = json.loads(self.state_management_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "freeze_primary_replay",
                "status": "continue",
                "reason": "late-preheat filtering and full-pre replay attachment did not beat the current primary frontier",
            },
            {
                "direction": "governance_stack",
                "status": "promote_to_authoritative_companion_surface",
                "reason": "timechain, failure library, intraday collapse supervision, phase state machine, and late-preheat mismatch now form a coherent oversight layer",
            },
            {
                "direction": "post_entry_state_management_template",
                "status": "prepare_for_cross_board_transfer",
                "reason": "commercial aerospace now has a compact, ordered state-management grammar that can be tested on another archetype without copying board-local windows",
            },
            {
                "direction": "further_board_local_replay_tuning",
                "status": "stop",
                "reason": "commercial-aerospace board-local replay tuning has reached diminishing returns and now risks turning into local curve carving",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129m_commercial_aerospace_klm_governance_packaging_triage_v1",
            "governance_layer_count": governance["summary"]["governance_layer_count"],
            "state_management_focus": state_management["summary"]["state_management_focus"],
            "authoritative_status": "freeze_commercial_aerospace_primary_plus_governance_and_shift_to_transfer_preparation",
            "authoritative_rule": "commercial-aerospace should now move from board-local replay tuning to governance-backed transfer preparation",
        }
        interpretation = [
            "V1.29M freezes the post-commercial-aerospace direction after replay-side and supervision-side work converged.",
            "The result is a two-part package: the frozen primary replay plus its governance/state-management companion surface.",
        ]
        return V129MCommercialAerospaceKLMGovernancePackagingTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129MCommercialAerospaceKLMGovernancePackagingTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129MCommercialAerospaceKLMGovernancePackagingTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129m_commercial_aerospace_klm_governance_packaging_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
