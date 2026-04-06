from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134fp_commercial_aerospace_add_day_level_selection_authority_audit_v1.json"
        )

    def analyze(self) -> V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_add_local_hierarchy_but_shift_next_to_day_level_selection_authority_supervision"
        )
        triage_rows = [
            {
                "component": "local_add_hierarchy",
                "status": "retain",
                "rationale": "the local permission family, confirmation layer, and full-quality archetype remain real inside supervision scope",
            },
            {
                "component": "broader_positive_add_promotion",
                "status": "still_blocked",
                "rationale": "the frontier now fails on day-level selection authority, not because the local archetype disappeared",
            },
            {
                "component": "next_supervision_direction",
                "status": "shift_to_day_level_selection_authority",
                "rationale": "the branch should now explain aligned, displaced, and post-wave-echo days instead of overfitting more local shape filters",
            },
        ]
        interpretation = [
            "V1.34FQ converts the day-level selection-authority audit into the next governance direction for the add frontier.",
            "The branch now knows that portable add permission requires a higher layer than local shape: it needs a credible day-level authority for why some strong symbols are selected, displaced, or ignored altogether.",
        ]
        return V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fq_commercial_aerospace_fp_day_level_selection_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "candidate_day_count": audit["summary"]["candidate_day_count"],
                "aligned_selection_day_count": audit["summary"]["aligned_selection_day_count"],
                "displaced_selection_day_count": audit["summary"]["displaced_selection_day_count"],
                "post_wave_echo_day_count": audit["summary"]["post_wave_echo_day_count"],
                "authoritative_rule": (
                    "the add branch should stop widening local shape and instead study day-level selection authority, because the remaining misses now live at the daily choice layer"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fq_commercial_aerospace_fp_day_level_selection_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
