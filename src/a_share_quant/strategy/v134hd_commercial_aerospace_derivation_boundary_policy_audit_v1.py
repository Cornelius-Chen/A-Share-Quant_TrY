from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Report:
    summary: dict[str, Any]
    policy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "policy_rows": self.policy_rows,
            "interpretation": self.interpretation,
        }


class V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.boundary_triage_path = analysis_dir / "v134hc_commercial_aerospace_hb_boundary_direction_triage_v1.json"
        self.vacancy_path = analysis_dir / "v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1.json"
        self.shadow_lane_path = analysis_dir / "v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1.json"
        self.bridge_spec_path = analysis_dir / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_derivation_boundary_policy_audit_v1.csv"
        )

    def analyze(self) -> V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Report:
        boundary_triage = json.loads(self.boundary_triage_path.read_text(encoding="utf-8"))
        vacancy = json.loads(self.vacancy_path.read_text(encoding="utf-8"))
        shadow_lane = json.loads(self.shadow_lane_path.read_text(encoding="utf-8"))
        bridge_spec = json.loads(self.bridge_spec_path.read_text(encoding="utf-8"))

        policy_rows = [
            {
                "policy_option": "implicit_auto_extension_from_raw",
                "status": "rejected",
                "rationale": (
                    "raw post-lockout dates exist, but auto-deriving board state from raw alone would silently reopen a frozen "
                    "lockout-aligned boundary without explicit governance approval"
                ),
            },
            {
                "policy_option": "explicit_boundary_extension_for_shadow_only",
                "status": "deferred_until_explicit_shift",
                "rationale": (
                    "extension is a legitimate future option, but only as an explicit shadow-lane policy change rather than an "
                    "incidental refresh"
                ),
            },
            {
                "policy_option": "retain_current_boundary",
                "status": "current_authoritative",
                "rationale": (
                    "current boundary remains the default because the shadow lane is protocol-only, execution stays blocked, and "
                    "post-lockout handoff still has zero lawful board-surface coverage"
                ),
            },
            {
                "policy_option": "unlock_classifier_debate_before_extension",
                "status": "rejected_ordering",
                "rationale": (
                    "arguing about post-lockout unlock quality before extending the board surfaces would invert the causal order"
                ),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(policy_rows[0].keys()))
            writer.writeheader()
            writer.writerows(policy_rows)

        summary = {
            "acceptance_posture": "freeze_v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1",
            "boundary_classification": boundary_triage["summary"]["boundary_classification"],
            "post_lockout_trade_date_count": vacancy["summary"]["post_lockout_trade_date_count"],
            "raw_only_vacancy_count": vacancy["summary"]["raw_only_vacancy_count"],
            "shadow_lane_state": shadow_lane["summary"]["frontier_state"],
            "bridge_stage_count": bridge_spec["summary"]["bridge_stage_count"],
            "current_policy": "retain_current_boundary",
            "future_policy_option": "explicit_boundary_extension_for_shadow_only",
            "policy_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "the current derivation boundary should remain frozen by default; any extension beyond lockout end must be an explicit "
                "shadow-only policy shift rather than an automatic refresh from existing raw data"
            ),
        }
        interpretation = [
            "V1.34HD converts the boundary classification into an explicit policy question.",
            "The conclusion is conservative by design: post-lockout extension is a possible future action, but only as an explicit shadow-lane boundary change, not as a silent continuation from raw coverage.",
        ]
        return V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Report(
            summary=summary,
            policy_rows=policy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
