from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124UCommercialAerospaceRSTTriageReport:
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
    result: V124UCommercialAerospaceRSTTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124UCommercialAerospaceRSTTriageReport(
        summary={
            "acceptance_posture": "freeze_v124u_commercial_aerospace_rst_triage_v1",
            "authoritative_status": "triage_refresh_success_but_core_thinning_required",
            "allow_control_extraction_now": False,
            "allow_replay_now": False,
            "authoritative_next_step": "control_authority_core_thinning_retriage",
        },
        reviewer_rows=[
            {
                "reviewer": "Pauli",
                "status": "triage_refresh_success_but_core_thinning_required",
                "allow_control_extraction_now": False,
                "key_point": "feed_ready_but_control_eligible_core_is_polluted_by_concept_and_mirror_names",
            },
            {
                "reviewer": "Tesla",
                "status": "triage_refresh_success_but_core_thinning_required",
                "allow_control_extraction_now": False,
                "key_point": "use_local_feed_refresh_as_input_only_then_thin_to_owner_only_core_before_controls",
            },
            {
                "reviewer": "James",
                "status": "data_ready_but_core_thinning_required",
                "allow_control_extraction_now": False,
                "key_point": "replay_is_still_blocked_by_control_core_legality_not_by_data",
            },
        ],
        interpretation=[
            "V1.24U freezes the three-subagent review of V124R/V124S/V124T.",
            "All three reviewers agree that the bottleneck has moved from data readiness to control-core legality.",
            "The next lawful step is a thinner authority-bounded re-triage, not replay and not control extraction on the current 16-name core.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124u_commercial_aerospace_rst_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
