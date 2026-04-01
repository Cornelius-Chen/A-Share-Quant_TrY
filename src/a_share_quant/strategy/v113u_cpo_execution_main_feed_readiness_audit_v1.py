from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113UCPOExecutionMainFeedReadinessAuditReport:
    summary: dict[str, Any]
    checks: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checks": self.checks,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113UCPOExecutionMainFeedReadinessAuditAnalyzer:
    def analyze(
        self,
        *,
        repo_root: Path,
        v112aa_payload: dict[str, Any],
        v113t_payload: dict[str, Any],
        v113q_payload: dict[str, Any],
    ) -> V113UCPOExecutionMainFeedReadinessAuditReport:
        cohort_rows = list(v112aa_payload.get("object_role_time_rows", []))
        t_summary = dict(v113t_payload.get("summary", {}))
        q_summary = dict(v113q_payload.get("summary", {}))
        if str(t_summary.get("acceptance_posture")) != "freeze_v113t_cpo_execution_main_feed_build_v1":
            raise ValueError("V1.13U expects V1.13T execution main feed build.")

        csv_path = repo_root / str(t_summary["output_csv"])
        with csv_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        symbols_in_feed = {str(row["symbol"]) for row in rows}
        expected_symbols = {str(row["symbol"]) for row in cohort_rows}
        checks = [
            {"check_name": "all_cohort_symbols_present", "passed": symbols_in_feed == expected_symbols},
            {"check_name": "time_sorted_csv", "passed": rows == sorted(rows, key=lambda r: (str(r["trade_date"]), str(r["symbol"])))},
            {"check_name": "listed_days_present", "passed": all(str(row["listed_days"]).strip() for row in rows)},
            {"check_name": "turnover_present", "passed": all(str(row["turnover"]).strip() for row in rows)},
            {"check_name": "t_plus_one_enabled", "passed": bool(q_summary.get("t_plus_one_enabled", False))},
        ]
        summary = {
            "acceptance_posture": "freeze_v113u_cpo_execution_main_feed_readiness_audit_v1",
            "board_name": "CPO",
            "execution_main_feed_ready_now": all(check["passed"] for check in checks),
            "execution_main_feed_symbol_count": len(symbols_in_feed),
            "recommended_next_posture": "bind_v113t_execution_main_feed_into_full_cpo_board_replay_if_internal_action_logic_is_available",
        }
        interpretation = [
            "V1.13U only audits feed completeness and legality. It does not claim that all 20 CPO symbols already have mature action logic.",
            "After V1.13T, the board-wide price feed itself can be ready even if strategy actions remain heterogeneous across symbols.",
            "This separates execution data readiness from full strategy maturity.",
        ]
        return V113UCPOExecutionMainFeedReadinessAuditReport(
            summary=summary,
            checks=checks,
            interpretation=interpretation,
        )


def write_v113u_cpo_execution_main_feed_readiness_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113UCPOExecutionMainFeedReadinessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
