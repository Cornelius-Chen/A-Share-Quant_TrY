from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123KCpoHijMarketRegimeTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123KCpoHijMarketRegimeTriageAnalyzer:
    def analyze(self) -> V123KCpoHijMarketRegimeTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "explanatory_only",
                "reason": "discovery_signal_exists_but_chronology_and_transfer_fail",
                "recommended_next_step": "keep_only_as_regime_explanation_layer_until_multi_year_index_data_exists",
            },
            {
                "reviewer": "Tesla",
                "verdict": "explanatory_only",
                "reason": "pooled_effect_cannot_overcome_time_split_collapse",
                "recommended_next_step": "no_candidate_or_replay_work_until_history_extends",
            },
            {
                "reviewer": "James",
                "verdict": "explanatory_only",
                "reason": "single_year_only_prevents_real_regime_generalization",
                "recommended_next_step": "retain_only_as_macro_explanatory_overlay",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123k_cpo_hij_market_regime_triage_v1",
            "related_runs": ["V123H", "V123I", "V123J"],
            "branch_name": "liquidity_drought_regime_score",
            "authoritative_status": "explanatory_only",
            "majority_vote": {"explanatory_only": 3},
            "replay_facing_allowed": False,
            "candidate_promotion_allowed": False,
            "recommended_next_posture": "retain_only_as_regime_explanatory_overlay_and_wait_for_multi_year_index_history",
        }
        interpretation = [
            "V1.23K freezes the broad market regime branch after discovery, chronology audit, and year evaluability check.",
            "The branch helps explain why major drawdown windows happened, but it is not stable enough to become a candidate overlay.",
            "Until multi-year index history exists, the branch stays in the explanatory layer only.",
        ]
        return V123KCpoHijMarketRegimeTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123KCpoHijMarketRegimeTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123KCpoHijMarketRegimeTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123k_cpo_hij_market_regime_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

