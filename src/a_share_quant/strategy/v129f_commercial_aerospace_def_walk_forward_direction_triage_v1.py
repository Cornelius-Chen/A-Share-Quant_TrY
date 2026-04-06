from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v129d_commercial_aerospace_phase_specific_walk_forward_support_audit_v1 import (
    V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer,
)
from a_share_quant.strategy.v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1 import (
    V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer,
)


@dataclass(slots=True)
class V129FCommercialAerospaceDEFWalkForwardDirectionTriageReport:
    summary: dict[str, Any]
    verdict_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "verdict_rows": self.verdict_rows,
            "interpretation": self.interpretation,
        }


class V129FCommercialAerospaceDEFWalkForwardDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V129FCommercialAerospaceDEFWalkForwardDirectionTriageReport:
        support = V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer(self.repo_root).analyze()
        pilot = V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer(self.repo_root).analyze()

        full_pre_row = next(row for row in pilot.fold_rows if row["target_state"] == "full_pre")
        full_row = next(row for row in pilot.fold_rows if row["target_state"] == "full")

        verdict_rows = [
            {
                "topic": "full_pre_phase_specific_supervision",
                "status": "retain_non_replay_research_path",
                "support_basis": "dedicated lawful fold exists on both sides and full_pre shows non-random but still noisy out-of-sample separation",
                "key_metric": full_pre_row["test_balanced_accuracy"],
            },
            {
                "topic": "full_phase_specific_supervision",
                "status": "keep_phase_contextual_not_directly_supervised",
                "support_basis": "dedicated fold exists but test positives remain too thin and out-of-sample separation is effectively random",
                "key_metric": full_row["test_balanced_accuracy"],
            },
            {
                "topic": "single_global_multiclass_reopen",
                "status": "blocked",
                "support_basis": "no single lawful split supports both full_pre and full on both train and test",
                "key_metric": 0.0,
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129f_commercial_aerospace_def_walk_forward_direction_triage_v1",
            "supported_walk_forward_fold_count": len(support.summary["supported_folds"]),
            "authoritative_status": "move_to_phase_specific_walk_forward_for_full_pre_only_and_keep_full_phase_contextual",
            "authoritative_rule": "commercial-aerospace supervision should stop treating full_pre/full as one jointly learnable class family under a single split and instead continue with phase-specific walk-forward only where lawful support exists",
        }
        interpretation = [
            "V1.29F freezes the next direction after the state-machine chronology blocker was clarified.",
            "The board should continue with phase-specific lawful research for full-pre, while full remains primarily phase-contextual until more repeated impulse cycles exist.",
        ]
        return V129FCommercialAerospaceDEFWalkForwardDirectionTriageReport(
            summary=summary,
            verdict_rows=verdict_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129FCommercialAerospaceDEFWalkForwardDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129FCommercialAerospaceDEFWalkForwardDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129f_commercial_aerospace_def_walk_forward_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
