from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12CatalystBranchPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12CatalystBranchPhaseCheckAnalyzer:
    """Check whether the bounded catalyst branch changes the main V1.2 phase posture."""

    def analyze(
        self,
        *,
        catalyst_audit_payload: dict[str, Any],
        bottleneck_check_payload: dict[str, Any],
    ) -> V12CatalystBranchPhaseCheckReport:
        catalyst_summary = dict(catalyst_audit_payload.get("summary", {}))
        bottleneck_summary = dict(bottleneck_check_payload.get("summary", {}))

        context_separation_present = bool(catalyst_summary.get("context_separation_present", False))
        keep_branch_report_only = bool(catalyst_summary.get("keep_branch_report_only", True))
        primary_bottleneck_still_carry = (
            str(bottleneck_summary.get("acceptance_posture", ""))
            == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        )

        summary = {
            "phase_posture": "keep_catalyst_branch_active_but_bounded",
            "context_separation_present": context_separation_present,
            "keep_branch_report_only": keep_branch_report_only,
            "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
            "catalyst_branch_changes_v12_direction_now": False,
            "promote_catalyst_branch_now": False,
            "recommended_next_posture": "preserve_catalyst_branch_as_context_support_not_mainline_switch",
        }
        evidence_rows = [
            {
                "evidence_name": "catalyst_directional_separation",
                "actual": {
                    "context_separation_present": context_separation_present,
                    "keep_branch_report_only": keep_branch_report_only,
                },
                "reading": "The catalyst branch is already directionally useful, but the bounded audit still keeps it below promotion threshold.",
            },
            {
                "evidence_name": "main_v12_bottleneck",
                "actual": {
                    "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
                },
                "reading": "Carry row diversity remains the main V1.2 bottleneck, so catalyst context should support rather than replace the current mainline.",
            },
        ]
        interpretation = [
            "The catalyst branch is now real enough to keep, but not strong enough to become the new V1.2 mainline.",
            "Its current value is contextual support: it helps explain why opening-led lanes surface before carry, without changing the carry-row-diversity bottleneck itself.",
            "So the correct phase reading is to preserve the branch as active but bounded and keep the mainline focused on true carry-row expansion.",
        ]
        return V12CatalystBranchPhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_catalyst_branch_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12CatalystBranchPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
