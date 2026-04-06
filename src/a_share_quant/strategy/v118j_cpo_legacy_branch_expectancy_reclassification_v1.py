from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class V118JCpoLegacyBranchExpectancyReclassificationReport:
    summary: dict[str, object]
    branch_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "branch_rows": self.branch_rows,
            "interpretation": self.interpretation,
        }


class V118JCpoLegacyBranchExpectancyReclassificationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V118JCpoLegacyBranchExpectancyReclassificationReport:
        summary = {
            "acceptance_posture": "freeze_v118j_cpo_legacy_branch_expectancy_reclassification_v1",
            "reclassification_scope": "discarded_or_degraded_cpo_branches_under_probability_expectancy_view",
            "soft_expectancy_component_count": 1,
            "explanatory_only_count": 3,
            "dead_count": 0,
            "restored_soft_expectancy_branch": "breakout_damage",
            "recommended_next_posture": "reuse_breakout_damage_only_as_soft_expectancy_penalty_not_as_candidate_branch",
        }
        branch_rows = [
            {
                "branch_name": "continuation_integrity",
                "new_classification": "explanatory_only",
                "reason": "Explains why q0.25 was cleaner than hot-only, but never created a reliable new execution constraint or training edge.",
            },
            {
                "branch_name": "reverse_signal_human_heuristic",
                "new_classification": "explanatory_only",
                "reason": "Reverse signal collapses on the conditioned main-uptrend surface and human heuristics remain protocol-level interaction aids.",
            },
            {
                "branch_name": "breakout_damage",
                "new_classification": "soft_expectancy_component",
                "reason": "Mainline and replay-facing status are dead, but the branch still retains enough learnability and false-positive explanatory value to survive as a soft expectancy penalty component.",
            },
            {
                "branch_name": "add_vs_entry",
                "new_classification": "explanatory_only",
                "reason": "The branch solved the right conceptual problem but actually tracked role-year pockets instead of a stable action distinction.",
            },
        ]
        interpretation = [
            "V1.18J revisits previously degraded CPO branches under a probability-expectancy framing instead of the older live-or-dead candidate framing.",
            "All three reviewers converged that only breakout-damage deserves to be rescued above pure explanation, and even then only as a soft expectancy component rather than a revived candidate branch.",
            "The other degraded lines remain explanatory only because they either never created real training gain or are dominated by role-year/object-shift artifacts.",
        ]
        return V118JCpoLegacyBranchExpectancyReclassificationReport(
            summary=summary,
            branch_rows=branch_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118JCpoLegacyBranchExpectancyReclassificationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118JCpoLegacyBranchExpectancyReclassificationAnalyzer(repo_root=repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118j_cpo_legacy_branch_expectancy_reclassification_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
