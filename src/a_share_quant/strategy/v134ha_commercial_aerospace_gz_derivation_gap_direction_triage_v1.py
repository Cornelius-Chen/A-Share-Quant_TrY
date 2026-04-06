from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1.json"
        )

    def analyze(self) -> V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "raw_intraday_calendar",
                "status": "retain",
                "rationale": "post-lockout raw coverage continues and should remain the calendar of record for the shadow lane",
            },
            {
                "component": "daily_state_surface",
                "status": "dominant_gap",
                "rationale": "board daily-state derivation stops exactly at lockout end and leaves all post-lockout raw dates uncovered",
            },
            {
                "component": "phase_geometry_surface",
                "status": "dominant_gap",
                "rationale": "phase geometry derivation stops at the same boundary, so unlock context cannot be evaluated on a synchronized board surface",
            },
            {
                "component": "synchronized_surface_stop",
                "status": "retain_as_primary_reading",
                "rationale": "the blocker is not a one-sided stale file but a coordinated derivation stop across both board surfaces",
            },
            {
                "component": "reentry_to_add_handoff",
                "status": "keep_blocked",
                "rationale": "handoff stays blocked until post-lockout board surfaces exist, regardless of continuing raw intraday coverage",
            },
        ]
        interpretation = [
            "V1.34HA turns the derivation-gap audit into the current governance reading for the shadow replay lane.",
            "The next blocker is now precise: the lane is not waiting on a better symbol clue but on extending both board-level derived surfaces past lockout end.",
        ]
        return V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134ha_commercial_aerospace_gz_derivation_gap_direction_triage_v1",
                "authoritative_status": (
                    "retain_board_surface_derivation_gap_audit_and_keep_shadow_bridge_blocked_until_post_lockout_board_surfaces_extend"
                ),
                "lockout_end_trade_date": audit["summary"]["lockout_end_trade_date"],
                "raw_last_trade_date": audit["summary"]["raw_last_trade_date"],
                "daily_last_trade_date": audit["summary"]["daily_last_trade_date"],
                "phase_last_trade_date": audit["summary"]["phase_last_trade_date"],
                "post_lockout_raw_trade_date_count": audit["summary"]["post_lockout_raw_trade_date_count"],
                "daily_post_lockout_gap_count": audit["summary"]["daily_post_lockout_gap_count"],
                "phase_post_lockout_gap_count": audit["summary"]["phase_post_lockout_gap_count"],
                "synchronized_surface_stop": audit["summary"]["synchronized_surface_stop"],
                "authoritative_rule": (
                    "the shadow bridge remains blocked because both board-level derivation surfaces stop exactly at lockout end "
                    "while raw post-lockout dates continue, so lawful unlock consultation has no synchronized board surface to read from"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ha_commercial_aerospace_gz_derivation_gap_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
