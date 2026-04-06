from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BCommercialAerospaceABSimulatorDirectionTriageReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    consensus_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "consensus_rows": self.consensus_rows,
            "interpretation": self.interpretation,
        }


class V134BCommercialAerospaceABSimulatorDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v134a_commercial_aerospace_intraday_execution_simulator_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ab_simulator_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BCommercialAerospaceABSimulatorDirectionTriageReport:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))

        review_rows = [
            {
                "reviewer": "Pasteur",
                "focus": "lawfulness",
                "verdict": "approved_if_next_bar_only",
                "hard_point": "the simulator must forbid same-bar execution and keep all tier actions on next-bar open fills only",
            },
            {
                "reviewer": "Sagan",
                "focus": "engineering_scope",
                "verdict": "approved_narrow_scope",
                "hard_point": "phase 2 should begin on canonical seed sessions only; do not widen to broader session simulation before seed reproducibility passes",
            },
            {
                "reviewer": "Dirac",
                "focus": "governance_boundary",
                "verdict": "approved_shadow_only",
                "hard_point": "phase 3 replay binding remains blocked; simulator outputs must stay explicitly shadow-only and read-only against the frozen EOD primary",
            },
        ]

        consensus_rows = [
            {
                "consensus_item": "phase_2_direction",
                "status": "approved_for_implementation",
                "detail": "the simulator specification is sufficiently explicit to begin implementation under the existing shadow-only guardrails",
            },
            {
                "consensus_item": "seed_scope_only",
                "status": "mandatory",
                "detail": "implementation starts on the six canonical seed sessions only; broader all-session simulation remains blocked",
            },
            {
                "consensus_item": "execution_clock",
                "status": "mandatory",
                "detail": "trigger at minute-close, fill at next-bar open, with no same-bar trading exceptions",
            },
            {
                "consensus_item": "phase_3_boundary",
                "status": "still_blocked",
                "detail": "separate intraday replay lane may not open until the simulator exists and passes a deterministic seed audit",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(consensus_rows[0].keys()))
            writer.writeheader()
            writer.writerows(consensus_rows)

        summary = {
            "acceptance_posture": "freeze_v134b_commercial_aerospace_ab_simulator_direction_triage_v1",
            "reviewer_count": len(review_rows),
            "consensus_count": len(consensus_rows),
            "spec_action_mapping_count": spec["summary"]["action_mapping_count"],
            "authoritative_status": "approve_phase_2_simulator_implementation_but_keep_phase_3_replay_lane_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34B converts the phase-2 simulator spec into an implementation triage result.",
            "The simulator may now be implemented, but only in the narrow seed-session shadow lane and without opening the replay-binding workstream.",
        ]
        return V134BCommercialAerospaceABSimulatorDirectionTriageReport(
            summary=summary,
            review_rows=review_rows,
            consensus_rows=consensus_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BCommercialAerospaceABSimulatorDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BCommercialAerospaceABSimulatorDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134b_commercial_aerospace_ab_simulator_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
