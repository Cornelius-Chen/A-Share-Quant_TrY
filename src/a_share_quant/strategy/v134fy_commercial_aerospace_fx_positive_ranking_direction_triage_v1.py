from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1.json"
        )

    def analyze(self) -> V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_active_wave_exclusion_but_block_positive_daily_ranker_promotion"
        )
        triage_rows = [
            {
                "component": "recent_reduce_residue_exclusion",
                "status": "retain",
                "rationale": "the negative same-wave exclusion clue is clean on the current local surface",
            },
            {
                "component": "positive_daily_ranker",
                "status": "not_yet_authorized",
                "rationale": "the retained selected states still split the positive metrics rather than collapsing into one dominant ranking clue",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "the frontier now owns a local exclusion clue, but it still lacks a justified positive daily ranker",
            },
        ]
        interpretation = [
            "V1.34FY turns the first positive-ranking audit into the current governance verdict for active-wave add selection.",
            "The branch should keep the new exclusion clue, but it should explicitly block positive ranker promotion until selected-state structure becomes more coherent than the current two-state split.",
        ]
        return V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fy_commercial_aerospace_fx_positive_ranking_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "selected_candidate_count": audit["summary"]["selected_candidate_count"],
                "same_symbol_higher_metric_count": audit["summary"]["same_symbol_higher_metric_count"],
                "clean_reset_higher_metric_count": audit["summary"]["clean_reset_higher_metric_count"],
                "authoritative_rule": (
                    "active-wave add selection now has a local exclusion clue but still lacks a promotable positive daily ranker"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FYCommercialAerospaceFXPositiveRankingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fy_commercial_aerospace_fx_positive_ranking_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
