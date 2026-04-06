from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V125KCommercialAerospaceIJKEventControlTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125KCommercialAerospaceIJKEventControlTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125KCommercialAerospaceIJKEventControlTriageReport(
        summary={
            "acceptance_posture": "freeze_v125k_commercial_aerospace_ijk_event_control_triage_v1",
            "authoritative_status": "event_conditioned_control_surface_partially_unblocked_but_still_not_lawful_for_replay",
            "allow_first_lawful_replay_now": False,
            "authoritative_next_step": "audit_event_coverage_gap_and_hybrid_bridge_before_any_replay",
            "best_variant": "quality_event_gate",
            "key_blockers": [
                "2024_has_zero_eligibility_flags_under_event_conditioning",
                "2026_eligibility_split_still_negative",
            ],
        },
        reviewer_rows=[
            {
                "reviewer": "Pauli",
                "status": "control_surface_partially_unblocked_but_not_lawful_yet",
                "allow_first_lawful_replay_now": False,
                "key_point": "quality_event_gate_fix_is_real_but_2024_has_zero_flags_and_2026_is_still_negative",
            },
            {
                "reviewer": "Tesla",
                "status": "control_surface_partially_unlocked_but_not_yet_lawful_for_replay",
                "allow_first_lawful_replay_now": False,
                "key_point": "mean_surface_is_fixed_but chronology_coverage_is_not_stable_enough_for_first_replay",
            },
            {
                "reviewer": "James",
                "status": "event_conditioned_control_surface_alive_but_not_fully_replay_promotable",
                "allow_first_lawful_replay_now": False,
                "key_point": "at_most_guarded_candidate_shadow_replay_not_first_lawful_replay",
            },
        ],
        interpretation=[
            "V1.25K freezes the three-subagent review of the event-conditioned commercial-aerospace control rebuild.",
            "The event layer clearly improved the control surface, but lawful replay remains blocked because chronology coverage is still broken at the tails.",
            "The next lawful step is understanding the 2024 zero-coverage gap and the 2026 weak tail before replay authorization.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125k_commercial_aerospace_ijk_event_control_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
