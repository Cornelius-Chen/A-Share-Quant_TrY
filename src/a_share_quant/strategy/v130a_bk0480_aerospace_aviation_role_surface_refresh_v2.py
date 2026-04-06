from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130ABK0480AerospaceAviationRoleSurfaceRefreshReport:
    summary: dict[str, Any]
    role_rows: list[dict[str, Any]]
    relative_structure_labels: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_rows": self.role_rows,
            "relative_structure_labels": self.relative_structure_labels,
            "interpretation": self.interpretation,
        }


class V130ABK0480AerospaceAviationRoleSurfaceRefreshAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.role_v1_path = repo_root / "reports" / "analysis" / "v129s_bk0480_aerospace_aviation_role_grammar_v1.json"
        self.triage_path = repo_root / "reports" / "analysis" / "v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1.json"
        self.audit_path = repo_root / "reports" / "analysis" / "v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1.json"

    def analyze(self) -> V130ABK0480AerospaceAviationRoleSurfaceRefreshReport:
        role_v1 = json.loads(self.role_v1_path.read_text(encoding="utf-8"))
        triage = json.loads(self.triage_path.read_text(encoding="utf-8"))
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        audit_rows = {row["symbol"]: row for row in audit["candidate_rows"]}

        role_rows = [
            {
                "symbol": "000738",
                "role_label": "stable_core_primary",
                "structural_authority": "board_internal_owner",
                "transfer_reset_posture": "local_snapshot_supported_v6",
                "rationale": "Remains the BK0480 internal authority until a wider harmonized control surface proves otherwise.",
            },
            {
                "symbol": "600118",
                "role_label": "high_quality_dual_core_support",
                "structural_authority": "board_internal_owner",
                "transfer_reset_posture": "local_snapshot_supported_v6",
                "rationale": "Remains the second internal owner and primary add/de-risk support surface.",
            },
            {
                "symbol": "600760",
                "role_label": "local_confirmation_candidate",
                "structural_authority": "confirmation_only",
                "transfer_reset_posture": "historical_native_support_v5_not_yet_harmonized_into_v6_control_surface",
                "rationale": audit_rows["600760"]["rationale"],
            },
            {
                "symbol": "002273",
                "role_label": "quarantine_pending_local_confirmation",
                "structural_authority": "quarantine_only",
                "transfer_reset_posture": "timeline_native_evidence_only",
                "rationale": audit_rows["002273"]["rationale"],
            },
            {
                "symbol": "601989",
                "role_label": "quarantine_pending_local_confirmation",
                "structural_authority": "quarantine_only",
                "transfer_reset_posture": "timeline_native_evidence_only",
                "rationale": audit_rows["601989"]["rationale"],
            },
            {
                "symbol": "000099",
                "role_label": "reject_or_mirror_pending",
                "structural_authority": "not_admitted",
                "transfer_reset_posture": "timeline_native_but_negative_mix",
                "rationale": audit_rows["000099"]["rationale"],
            },
        ]

        relative_structure_labels = [
            {"label_name": "internal_owner_stack", "members": ["000738", "600118"], "meaning": "still the only names allowed to define authority/support semantics"},
            {"label_name": "confirmation_stack", "members": ["600760"], "meaning": "historically strong BK0480-native confirmation name, but not yet a control-authority participant"},
            {"label_name": "quarantine_stack", "members": ["002273", "601989"], "meaning": "watchlist names with BK0480-native evidence that need more harmonized local support before admission"},
            {"label_name": "reject_or_mirror_pending_stack", "members": ["000099"], "meaning": "currently too mixed or negative for admission; only retained as a local rejection case"},
        ]

        summary = {
            "acceptance_posture": "freeze_v130a_bk0480_aerospace_aviation_role_surface_refresh_v2",
            "board_name": role_v1["summary"]["board_name"],
            "sector_id": role_v1["summary"]["sector_id"],
            "internal_owner_count": 2,
            "confirmation_count": 1,
            "quarantine_count": 2,
            "reject_pending_count": 1,
            "source_boundary": triage["summary"]["authoritative_rule"],
            "next_phase": "control_surface_refresh_with_feed_harmonization_guard",
            "recommended_next_posture": "refresh_bk0480_control_surface_without_granting_600760_authority_until_cross_version_semantics_are_harmonized",
        }
        interpretation = [
            "V1.30A widens BK0480 from a pure dual-core board to a dual-core-plus-confirmation surface.",
            "600760 is admitted only as confirmation because its strongest evidence comes from historical BK0480-native support, not the current v6 owner surface.",
            "002273 and 601989 remain quarantined to preserve transfer discipline and avoid replay leakage from weak local evidence.",
        ]
        return V130ABK0480AerospaceAviationRoleSurfaceRefreshReport(summary=summary, role_rows=role_rows, relative_structure_labels=relative_structure_labels, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V130ABK0480AerospaceAviationRoleSurfaceRefreshReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130ABK0480AerospaceAviationRoleSurfaceRefreshAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130a_bk0480_aerospace_aviation_role_surface_refresh_v2",
        result=result,
    )


if __name__ == "__main__":
    main()
