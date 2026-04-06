from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130EBK0480AerospaceAviationHistoricalBridgeFormalizationReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


class V130EBK0480AerospaceAviationHistoricalBridgeFormalizationAnalyzer:
    TARGET_SYMBOL = "600760"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.expansion_audit_path = (
            repo_root / "reports" / "analysis" / "v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1.json"
        )
        self.harmonization_path = (
            repo_root / "reports" / "analysis" / "v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1.json"
        )
        self.timeline_path = repo_root / "reports" / "analysis" / "market_v5_q2_symbol_timeline_600760_capture_b_v1.json"
        self.specialist_opening_path = (
            repo_root / "reports" / "analysis" / "market_v5_q2_specialist_window_opening_600760_b_v1.json"
        )
        self.specialist_persistence_path = (
            repo_root / "reports" / "analysis" / "market_v5_q2_specialist_window_persistence_600760_b_v1.json"
        )
        self.second_lane_path = (
            repo_root / "reports" / "analysis" / "market_v5_q2_second_lane_acceptance_600760_v1.json"
        )

    def analyze(self) -> V130EBK0480AerospaceAviationHistoricalBridgeFormalizationReport:
        expansion = json.loads(self.expansion_audit_path.read_text(encoding="utf-8"))
        harmonization = json.loads(self.harmonization_path.read_text(encoding="utf-8"))
        timeline = json.loads(self.timeline_path.read_text(encoding="utf-8"))
        specialist_opening = json.loads(self.specialist_opening_path.read_text(encoding="utf-8"))
        specialist_persistence = json.loads(self.specialist_persistence_path.read_text(encoding="utf-8"))
        second_lane = json.loads(self.second_lane_path.read_text(encoding="utf-8"))

        expansion_row = next(row for row in expansion["candidate_rows"] if row["symbol"] == self.TARGET_SYMBOL)
        harmonization_row = next(row for row in harmonization["candidate_rows"] if row["symbol"] == self.TARGET_SYMBOL)

        approved_dates = sorted(
            {
                row["trade_date"]
                for record in timeline["candidate_records"]
                for row in record["daily_records"]
                if row.get("approved_sector_id") == "BK0480"
            }
        )
        bridge_strength = round(
            (
                min(expansion_row["v5_snapshot_days"], 50) / 50.0
                + expansion_row["timeline_leader_core_days"] / max(expansion_row["timeline_approval_days"], 1)
                + min(expansion_row["timeline_buy_days"], 4) / 4.0
            )
            / 3.0,
            6,
        )

        evidence_rows = [
            {
                "evidence_name": "historical_snapshot_support",
                "actual": {
                    "v5_snapshot_days": expansion_row["v5_snapshot_days"],
                    "v5_mean_non_junk": expansion_row["v5_mean_non_junk"],
                    "v5_mean_expected_upside": expansion_row["v5_mean_expected_upside"],
                },
                "reading": "600760 had real BK0480-native support on the historical v5 plane, not just stray timeline mentions.",
            },
            {
                "evidence_name": "timeline_permission_support",
                "actual": {
                    "timeline_approval_days": expansion_row["timeline_approval_days"],
                    "timeline_leader_core_days": expansion_row["timeline_leader_core_days"],
                    "timeline_buy_days": expansion_row["timeline_buy_days"],
                    "approved_dates": approved_dates,
                },
                "reading": "The timeline evidence is strong enough to retain 600760 as a local historical confirmation bridge.",
            },
            {
                "evidence_name": "same_plane_harmonization_gap",
                "actual": {
                    "v6_snapshot_days": expansion_row["v6_snapshot_days"],
                    "harmonization_status": harmonization_row["harmonization_status"],
                },
                "reading": "The bridge is not same-plane harmonized, so it cannot directly enter current control-surface math.",
            },
            {
                "evidence_name": "specialist_window_quality",
                "actual": {
                    "specialist_opened_window": specialist_opening["summary"]["specialist_opened_window"],
                    "specialist_preserved_window": specialist_persistence["summary"]["specialist_preserved_window"],
                    "second_lane_acceptance_posture": second_lane["summary"]["acceptance_posture"],
                    "target_pnl_delta": second_lane["summary"]["target_pnl_delta"],
                },
                "reading": "The bridge is structurally real but not acceptance-grade for replay unlock; prior lane work did not surface a clean opening or persistence edge.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1",
            "board_name": harmonization["summary"]["board_name"],
            "sector_id": harmonization["summary"]["sector_id"],
            "target_symbol": self.TARGET_SYMBOL,
            "bridge_strength": bridge_strength,
            "harmonization_status": harmonization_row["harmonization_status"],
            "specialist_opened_window": specialist_opening["summary"]["specialist_opened_window"],
            "specialist_preserved_window": specialist_persistence["summary"]["specialist_preserved_window"],
            "second_lane_acceptance_grade": False,
            "authoritative_status": "retain_600760_as_historical_confirmation_bridge_only",
            "authoritative_rule": "600760_is_strong_enough_to_remain_the_only_bk0480_historical_bridge_but_not_strong_enough_to_unlock_control_authority_or_replay",
            "recommended_next_posture": "triage_whether_to_freeze_bk0480_here_or_keep_waiting_for_v6_native_support",
        }
        interpretation = [
            "V1.30E formalizes 600760 as the only credible BK0480 historical bridge candidate.",
            "The bridge is real enough to keep in confirmation language and portability memory, but not clean enough to count as replay-unlocking evidence.",
        ]
        return V130EBK0480AerospaceAviationHistoricalBridgeFormalizationReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130EBK0480AerospaceAviationHistoricalBridgeFormalizationReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130EBK0480AerospaceAviationHistoricalBridgeFormalizationAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
