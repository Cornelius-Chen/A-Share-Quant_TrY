from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V116AThreeRunAdversarialReviewCadenceProtocolReport:
    summary: dict[str, Any]
    cadence_rules: list[dict[str, Any]]
    current_triage_window: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cadence_rules": self.cadence_rules,
            "current_triage_window": self.current_triage_window,
            "interpretation": self.interpretation,
        }


class V116AThreeRunAdversarialReviewCadenceProtocolAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V116AThreeRunAdversarialReviewCadenceProtocolReport:
        triage_window = ["V115P", "V115Q", "V115R"]
        cadence_rules = [
            {
                "rule_id": "every_three_runs_force_adversarial_review",
                "trigger": "three_consecutive_new_runs_completed",
                "required_reviewers": 3,
                "review_axes": [
                    "methodology_and_overfit",
                    "execution_and_timing_realism",
                    "training_and_label_quality",
                ],
                "promotion_gate": "no_new_promotion_without_triage_pass",
            },
            {
                "rule_id": "triage_is_audit_not_promotion",
                "trigger": "triage_window_locked",
                "required_output": [
                    "keep",
                    "do_not_promote",
                    "single_most_important_next_constraint",
                ],
                "note": "subagent review can narrow or freeze, but cannot by itself promote new law",
            },
            {
                "rule_id": "triage_rolls_forward",
                "trigger": "triage_completed",
                "next_window_rule": "start_counting_next_three_runs_after_current_triage",
                "note": "prevent infinite drift and ensure cadence remains periodic rather than ad hoc",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v116a_three_run_adversarial_review_cadence_protocol_v1",
            "cadence_interval_runs": 3,
            "required_reviewers": 3,
            "current_triage_window_size": len(triage_window),
            "current_triage_window_start": triage_window[0],
            "current_triage_window_end": triage_window[-1],
            "recommended_next_posture": "bind_adversarial_triage_after_every_three_new_runs_before_any_promotion_step",
        }
        interpretation = [
            "V1.16A formalizes a recurring anti-drift checkpoint: every three consecutive runs, force a three-angle adversarial review before allowing new promotion steps.",
            "The triage is not another source of promotion; it is a brake against local overconfidence and execution drift.",
            "The first active window under this cadence is V115P/V115Q/V115R.",
        ]
        return V116AThreeRunAdversarialReviewCadenceProtocolReport(
            summary=summary,
            cadence_rules=cadence_rules,
            current_triage_window={
                "run_ids": triage_window,
                "status": "active_now",
            },
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116AThreeRunAdversarialReviewCadenceProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116AThreeRunAdversarialReviewCadenceProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116a_three_run_adversarial_review_cadence_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
