from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1.json"
        )

    def analyze(self) -> V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "post_lockout_raw_calendar",
                "status": "retain",
                "rationale": "post-lockout local intraday dates do exist, so the vacancy is not a raw-data absence",
            },
            {
                "component": "derived_board_surface",
                "status": "dominant_blocker",
                "rationale": "every post-lockout raw trading date still lacks the derived board-state surface needed to evaluate unlock context",
            },
            {
                "component": "unlock_context",
                "status": "keep_absent",
                "rationale": "without post-lockout derived board coverage there can be no lawful unlock-positive or unlock-worthy context",
            },
            {
                "component": "reentry_to_add_handoff",
                "status": "keep_blocked",
                "rationale": "handoff remains blocked because the bridge has no post-lockout board surface to reopen into",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "this vacancy audit clarifies a missing context layer and does not promote execution",
            },
        ]
        interpretation = [
            "V1.34GY converts the vacancy audit into the current governance verdict for the shadow replay lane.",
            "The next blocker is now narrower than before: post-lockout local dates exist, but the board-level derived surface has not been extended beyond lockout end, so unlock consultation cannot yet restart.",
        ]
        return V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gy_commercial_aerospace_gx_unlock_vacancy_direction_triage_v1",
                "authoritative_status": (
                    "retain_post_lockout_unlock_vacancy_audit_and_keep_handoff_blocked_until_post_lockout_board_surface_exists"
                ),
                "lockout_end_trade_date": audit["summary"]["lockout_end_trade_date"],
                "post_lockout_trade_date_count": audit["summary"]["post_lockout_trade_date_count"],
                "derived_board_surface_present_count": audit["summary"]["derived_board_surface_present_count"],
                "raw_only_vacancy_count": audit["summary"]["raw_only_vacancy_count"],
                "post_lockout_unlock_positive_count": audit["summary"]["post_lockout_unlock_positive_count"],
                "post_lockout_unlock_worthy_count": audit["summary"]["post_lockout_unlock_worthy_count"],
                "authoritative_rule": (
                    "reentry-to-add handoff stays blocked after lockout not because raw dates disappear but because post-lockout "
                    "board-state derivation has not yet produced any surface on which unlock context could be judged"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gy_commercial_aerospace_gx_unlock_vacancy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
