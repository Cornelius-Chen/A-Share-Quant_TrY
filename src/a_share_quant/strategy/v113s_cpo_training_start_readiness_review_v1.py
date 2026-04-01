from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113SCPOTrainingStartReadinessReviewReport:
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


class V113SCPOTrainingStartReadinessReviewAnalyzer:
    def analyze(
        self,
        *,
        v113q_payload: dict[str, Any],
        v113r_payload: dict[str, Any],
    ) -> V113SCPOTrainingStartReadinessReviewReport:
        q_summary = dict(v113q_payload.get("summary", {}))
        r_summary = dict(v113r_payload.get("summary", {}))
        if str(q_summary.get("acceptance_posture")) != "freeze_v113q_cpo_training_material_readiness_audit_v1":
            raise ValueError("V1.13S expects V1.13Q readiness audit.")
        if str(r_summary.get("acceptance_posture")) != "freeze_v113r_cpo_full_board_daily_bar_proxy_completion_v1":
            raise ValueError("V1.13S expects V1.13R proxy completion.")

        checks = [
            {"check_name": "time_order_ready", "passed": bool(q_summary.get("time_order_ready", False))},
            {"check_name": "full_board_proxy_daily_bars_complete", "passed": int(r_summary.get("proxy_completed_symbol_count", 0)) == int(r_summary.get("cohort_symbol_count", -1))},
            {"check_name": "proxy_training_use_allowed", "passed": bool(r_summary.get("training_use_allowed", False))},
            {"check_name": "execution_still_not_on_proxy", "passed": not bool(r_summary.get("execution_use_allowed", True))},
        ]
        training_ready = all(check["passed"] for check in checks)
        summary = {
            "acceptance_posture": "freeze_v113s_cpo_training_start_readiness_review_v1",
            "board_name": "CPO",
            "board_level_training_ready_now": training_ready,
            "execution_level_full_board_ready_now": False,
            "recommended_training_posture": "start_board_level_cpo_training_on_time_sorted_no_leak_seed_plus_proxy_full_board_daily_bars",
            "recommended_execution_posture": "do_not_claim_full_board_execution_readiness_until_stricter_market_feed_and_internal_action_labels_are completed",
        }
        interpretation = [
            "V1.13S distinguishes training readiness from execution readiness.",
            "After V1.13R, CPO can start board-level training with full-board proxy daily bars plus the already time-sorted no-leak seed tables.",
            "This does not mean the full board is execution-ready; the proxy feed remains training-only.",
        ]
        return V113SCPOTrainingStartReadinessReviewReport(
            summary=summary,
            checks=checks,
            interpretation=interpretation,
        )


def write_v113s_cpo_training_start_readiness_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113SCPOTrainingStartReadinessReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
