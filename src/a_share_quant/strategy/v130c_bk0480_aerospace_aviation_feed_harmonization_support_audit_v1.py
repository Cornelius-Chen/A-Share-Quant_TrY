from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1.json"
        self.role_surface_path = repo_root / "reports" / "analysis" / "v130a_bk0480_aerospace_aviation_role_surface_refresh_v2.json"

    def analyze(self) -> V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        role_surface = json.loads(self.role_surface_path.read_text(encoding="utf-8"))

        audit_rows = {row["symbol"]: row for row in audit["candidate_rows"]}
        review_symbols = ["600760", "002273", "601989", "000099"]
        candidate_rows = []
        same_plane_support_count = 0
        historical_bridge_count = 0
        timeline_only_count = 0
        for symbol in review_symbols:
            row = audit_rows[symbol]
            v6_supported = row["v6_snapshot_days"] > 0
            v5_supported = row["v5_snapshot_days"] > 0
            timeline_supported = row["timeline_approval_days"] > 0
            if v6_supported:
                harmonization_status = "same_plane_ready"
                same_plane_support_count += 1
            elif v5_supported and timeline_supported:
                harmonization_status = "historical_bridge_only"
                historical_bridge_count += 1
            elif timeline_supported:
                harmonization_status = "timeline_only"
                timeline_only_count += 1
            else:
                harmonization_status = "unsupported"
            candidate_rows.append(
                {
                    "symbol": symbol,
                    "role_label": next(item["role_label"] for item in role_surface["role_rows"] if item["symbol"] == symbol),
                    "v5_snapshot_days": row["v5_snapshot_days"],
                    "v6_snapshot_days": row["v6_snapshot_days"],
                    "timeline_approval_days": row["timeline_approval_days"],
                    "harmonization_status": harmonization_status,
                    "harmonization_risk": (
                        "no_same_plane_v6_support_for_control_math"
                        if harmonization_status != "same_plane_ready"
                        else "none"
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1",
            "board_name": role_surface["summary"]["board_name"],
            "sector_id": role_surface["summary"]["sector_id"],
            "review_symbol_count": len(candidate_rows),
            "same_plane_support_count": same_plane_support_count,
            "historical_bridge_only_count": historical_bridge_count,
            "timeline_only_count": timeline_only_count,
            "authoritative_rule": "bk0480_cannot_refresh_a_wider_control_surface_until_non_core_names_have_same_plane_support_or_an_explicitly_harmonized_bridge",
            "recommended_next_posture": "freeze_role_surface_v2_and_block_replay_or_control_refresh_until_more_v6_native_support_exists",
        }
        interpretation = [
            "V1.30C audits whether BK0480 non-core names can be legally folded into the current control-surface math.",
            "600760 is strong enough to enter confirmation language, but it is still only a historical bridge candidate rather than a same-plane v6 control participant.",
            "No non-core name currently has same-plane support, so control-surface widening remains blocked.",
        ]
        return V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditReport(summary=summary, candidate_rows=candidate_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
