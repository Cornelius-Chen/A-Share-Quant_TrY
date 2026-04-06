from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122UCpo1MinDownsideAttachmentStoplineReport:
    summary: dict[str, Any]
    decision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "decision_rows": self.decision_rows,
            "interpretation": self.interpretation,
        }


class V122UCpo1MinDownsideAttachmentStoplineAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122UCpo1MinDownsideAttachmentStoplineReport:
        v122s = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122s_cpo_1min_historical_bridge_overlap_audit_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v122t = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122t_cpo_1min_downside_same_plane_stack_audit_v1.json").read_text(
                encoding="utf-8"
            )
        )

        direct_historical_bridge_allowed = bool(v122s["summary"]["direct_historical_bridge_allowed"])
        stack_improves_over_base = bool(v122t["summary"]["stack_improves_over_base"])

        decision_rows = [
            {
                "decision_name": "direct_historical_bridge",
                "allowed": direct_historical_bridge_allowed,
                "reason": "date_overlap_required_between_recent_1min_and_historical_reduce_surface",
            },
            {
                "decision_name": "recent_same_plane_stack_attachment",
                "allowed": stack_improves_over_base,
                "reason": "stack_must_improve_discovery_and_transfer_together",
            },
            {
                "decision_name": "retain_1min_downside_component",
                "allowed": True,
                "reason": "standalone_soft_component_still_has_positive_but_weak_signal",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v122u_cpo_1min_downside_attachment_stopline_v1",
            "direct_historical_bridge_allowed": direct_historical_bridge_allowed,
            "recent_same_plane_stack_attachment_allowed": stack_improves_over_base,
            "standalone_1min_downside_soft_component_retained": True,
            "attachment_posture": (
                "defer_until_historical_1min_or_better_same_plane_increment_exists"
                if (not direct_historical_bridge_allowed and not stack_improves_over_base)
                else "conditional_attachment_review_open"
            ),
            "recommended_next_posture": "three_run_adversarial_review_for_attachment_decision",
        }
        interpretation = [
            "V1.22U freezes the bridge decision rather than letting the project quietly smuggle the recent 1-minute downside line into the broader risk stack.",
            "If the historical bridge is impossible and the recent same-plane stack does not clearly improve over base, attachment must be deferred.",
            "The correct retained object is the standalone 1-minute downside soft component, not a pretend integrated rule.",
        ]
        return V122UCpo1MinDownsideAttachmentStoplineReport(
            summary=summary,
            decision_rows=decision_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122UCpo1MinDownsideAttachmentStoplineReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122UCpo1MinDownsideAttachmentStoplineAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122u_cpo_1min_downside_attachment_stopline_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
