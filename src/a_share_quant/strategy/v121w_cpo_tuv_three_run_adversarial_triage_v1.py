from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V121WCpoTuvThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V121WCpoTuvThreeRunAdversarialTriageAnalyzer:
    def analyze(self) -> V121WCpoTuvThreeRunAdversarialTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "judgement": "correct_next_research_mainline_non_replay_only",
                "biggest_risk": "9-day recency overfit",
                "recommended_next_step": "1min_microstructure_discovery_and_adversarial_audit",
            },
            {
                "reviewer": "Tesla",
                "judgement": "correct_next_research_mainline_non_replay_only",
                "biggest_risk": "8-trading-day microstructure hallucination",
                "recommended_next_step": "1min_microstructure_discovery_and_adversarial_audit",
            },
            {
                "reviewer": "James",
                "judgement": "correct_next_research_mainline_non_replay_only",
                "biggest_risk": "tiny recent sample with no action labels yet",
                "recommended_next_step": "1min_action_timepoint_labeling_then_discovery",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v121w_cpo_tuv_three_run_adversarial_triage_v1",
            "authoritative_status": "1min_plane_confirmed_as_next_research_mainline_non_replay_only",
            "reviewer_consensus": "unanimous",
            "main_risk": "recent_sample_recency_overfit",
            "forbidden_next_step": "any_replay_promotion_or_shadow_replay",
            "recommended_next_posture": "1min_microstructure_discovery_on_feature_table",
        }
        interpretation = [
            "All three adversarial reviewers agree the recent 1-minute plane is the correct next research mainline for CPO.",
            "All three also agree the immediate risk is recency overfit because the window is short and the symbol set is narrow.",
            "The next step is 1-minute discovery and audit, not replay promotion.",
        ]
        return V121WCpoTuvThreeRunAdversarialTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121WCpoTuvThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121WCpoTuvThreeRunAdversarialTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121w_cpo_tuv_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
