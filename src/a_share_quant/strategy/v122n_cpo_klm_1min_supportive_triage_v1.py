from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122NCpoKlm1MinSupportiveTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V122NCpoKlm1MinSupportiveTriageAnalyzer:
    def analyze(self) -> V122NCpoKlm1MinSupportiveTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "supportive_continuation_status": "explanatory_only",
                "reason": "add_reduce_separation_fails_under_time_split",
                "recommended_next_step": "shift_1min_plane_to_downside_reduce_close_microstructure",
            },
            {
                "reviewer": "Tesla",
                "supportive_continuation_status": "explanatory_only",
                "reason": "gap_too_small_and_chronology_near_random",
                "recommended_next_step": "shift_1min_plane_to_downside_reduce_close_microstructure",
            },
            {
                "reviewer": "James",
                "supportive_continuation_status": "explanatory_only",
                "reason": "cannot_be_narrowed_into_clean_add_rule",
                "recommended_next_step": "shift_1min_plane_to_downside_reduce_close_microstructure",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v122n_cpo_klm_1min_supportive_triage_v1",
            "supportive_continuation_status": "explanatory_only",
            "reviewer_consensus": "unanimous",
            "forbidden_next_step": "any_further_same_family_add_side_tuning_or_replay",
            "recommended_next_posture": "recenter_1min_plane_on_downside_reduce_close_microstructure",
        }
        interpretation = [
            "The supportive continuation 1-minute family can no longer be treated as a surviving add-side candidate after the failed add-vs-reduce separation attempt.",
            "It is retained only as explanatory microstructure context.",
            "The correct next step is to shift the 1-minute plane away from add-side tuning and toward downside/reduce/close-side microstructure audit.",
        ]
        return V122NCpoKlm1MinSupportiveTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122NCpoKlm1MinSupportiveTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122NCpoKlm1MinSupportiveTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122n_cpo_klm_1min_supportive_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
