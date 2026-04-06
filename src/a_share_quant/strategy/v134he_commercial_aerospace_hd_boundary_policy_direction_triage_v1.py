from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
        )

    def analyze(self) -> V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "current_boundary",
                "status": "retain",
                "rationale": "the current lockout-aligned derivation boundary remains the authoritative default",
            },
            {
                "component": "implicit_auto_extension",
                "status": "keep_rejected",
                "rationale": "existing raw coverage does not justify silently extending a frozen board-surface boundary",
            },
            {
                "component": "explicit_shadow_only_extension",
                "status": "future_option_only",
                "rationale": "extension remains a possible future move, but only through an explicit shadow-lane policy shift",
            },
            {
                "component": "unlock_quality_debate",
                "status": "defer_until_boundary_changes",
                "rationale": "post-lockout unlock quality should not be debated before the boundary policy itself is changed",
            },
            {
                "component": "shadow_bridge",
                "status": "keep_blocked",
                "rationale": "the bridge remains blocked while the derivation boundary stays frozen",
            },
        ]
        interpretation = [
            "V1.34HE turns the boundary-policy audit into the current governance direction.",
            "The next meaningful move is now policy-level, not signal-level: either keep the lockout-aligned boundary frozen or later open an explicit shadow-only extension program.",
        ]
        return V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134he_commercial_aerospace_hd_boundary_policy_direction_triage_v1",
                "authoritative_status": (
                    "retain_lockout_aligned_derivation_boundary_as_default_and_require_explicit_shadow_only_policy_shift_for_any_extension"
                ),
                "boundary_classification": audit["summary"]["boundary_classification"],
                "post_lockout_trade_date_count": audit["summary"]["post_lockout_trade_date_count"],
                "raw_only_vacancy_count": audit["summary"]["raw_only_vacancy_count"],
                "shadow_lane_state": audit["summary"]["shadow_lane_state"],
                "current_policy": audit["summary"]["current_policy"],
                "future_policy_option": audit["summary"]["future_policy_option"],
                "authoritative_rule": (
                    "until an explicit shadow-only extension program is opened, the lockout-aligned derivation boundary remains "
                    "the authoritative stop and the shadow bridge stays blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134he_commercial_aerospace_hd_boundary_policy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
