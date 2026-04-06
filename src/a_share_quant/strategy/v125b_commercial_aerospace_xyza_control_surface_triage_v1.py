from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V125BCommercialAerospaceXYZAControlSurfaceTriageReport:
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
    result: V125BCommercialAerospaceXYZAControlSurfaceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125BCommercialAerospaceXYZAControlSurfaceTriageReport(
        summary={
            "acceptance_posture": "freeze_v125b_commercial_aerospace_xyza_control_surface_triage_v1",
            "authoritative_status": "role_grammar_ready_but_control_surface_not_replayable",
            "allow_first_lawful_replay_now": False,
            "authoritative_next_step": "control_semantics_narrowing",
        },
        reviewer_rows=[
            {
                "reviewer": "Pauli",
                "status": "role_grammar_ready_but_control_surface_not_lawful_yet",
                "allow_first_lawful_replay_now": False,
                "key_point": "time_split_signals_are_negative_or_flat_so_replay_remains_blocked",
            },
            {
                "reviewer": "Tesla",
                "status": "control_surface_defined_but_not_lawful_for_replay",
                "allow_first_lawful_replay_now": False,
                "key_point": "eligibility_edge_is_too_small_and_de_risk_direction_is_wrong",
            },
            {
                "reviewer": "James",
                "status": "role_grammar_ready_but_control_surface_not_replayable",
                "allow_first_lawful_replay_now": False,
                "key_point": "redefine_eligibility_and_de_risk_before_any_paper_replay",
            },
        ],
        interpretation=[
            "V1.25B freezes the subagent review of the refreshed role grammar and the first rolling control audit.",
            "Commercial aerospace is now structurally readable, but its first control semantics are still too weak for lawful replay.",
            "The next step is narrowing the semantics, not forcing replay.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125b_commercial_aerospace_xyza_control_surface_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
