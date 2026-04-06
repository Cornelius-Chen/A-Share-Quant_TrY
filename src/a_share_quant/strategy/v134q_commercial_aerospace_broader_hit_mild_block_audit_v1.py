from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134l_commercial_aerospace_intraday_broader_hit_simulator_v1 import (
    V134LCommercialAerospaceIntradayBroaderHitSimulatorAnalyzer,
)


@dataclass(slots=True)
class V134QCommercialAerospaceBroaderHitMildBlockAuditReport:
    summary: dict[str, Any]
    compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "compare_rows": self.compare_rows,
            "interpretation": self.interpretation,
        }


class V134QCommercialAerospaceBroaderHitMildBlockAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_report_path = (
            repo_root / "reports" / "analysis" / "v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.json"
        )
        self.output_sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_mild_block_sessions_v1.csv"
        )

    def analyze(self) -> V134QCommercialAerospaceBroaderHitMildBlockAuditReport:
        base = json.loads(self.base_report_path.read_text(encoding="utf-8"))
        analyzer = V134LCommercialAerospaceIntradayBroaderHitSimulatorAnalyzer(self.repo_root)
        widened = analyzer.analyze()

        adjusted_session_rows = []
        simulated_order_count = 0
        reversal_execution_count = 0
        severe_execution_count = 0
        same_day_loss_avoided_total = 0.0
        blocked_mild_session_count = 0

        for row in widened.session_rows:
            copied = dict(row)
            if copied["predicted_tier"] == "mild_override_watch":
                blocked_mild_session_count += 1
                copied["filled_step_count"] = 0
                copied["remaining_quantity_after_sim"] = copied["reference_quantity"]
                copied["simulated_pnl"] = copied["baseline_hold_pnl"]
                copied["same_day_loss_avoided"] = 0.0
                copied["simulated_close_value"] = round(copied["reference_quantity"] * copied["close_price"], 4)
            else:
                simulated_order_count += copied["filled_step_count"]
                if copied["first_reversal_minute"] != "":
                    reversal_execution_count += 1
                if copied["first_severe_minute"] != "":
                    severe_execution_count += 1
            same_day_loss_avoided_total += float(copied["same_day_loss_avoided"])
            adjusted_session_rows.append(copied)

        self.output_sessions_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_sessions_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(adjusted_session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(adjusted_session_rows)

        compare_rows = [
            {
                "variant": "base_broader_hit",
                "same_day_loss_avoided_total": base["summary"]["same_day_loss_avoided_total"],
                "simulated_order_count": base["summary"]["simulated_order_count"],
            },
            {
                "variant": "mild_blocked_broader_hit",
                "same_day_loss_avoided_total": round(same_day_loss_avoided_total, 4),
                "simulated_order_count": simulated_order_count,
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1",
            "base_same_day_loss_avoided_total": base["summary"]["same_day_loss_avoided_total"],
            "mild_block_same_day_loss_avoided_total": round(same_day_loss_avoided_total, 4),
            "same_day_loss_avoided_delta": round(same_day_loss_avoided_total - float(base["summary"]["same_day_loss_avoided_total"]), 4),
            "base_simulated_order_count": base["summary"]["simulated_order_count"],
            "mild_block_simulated_order_count": simulated_order_count,
            "blocked_mild_session_count": blocked_mild_session_count,
            "sessions_csv": str(self.output_sessions_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_hit_mild_block_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34Q evaluates the exact boundary change recommended by the broader-hit supervision review: block execution for predicted mild sessions inside the wider phase-2 lane.",
            "The audit is deliberately narrow so the next direction judgment can focus on whether this one refinement improves the wider lane without changing its clock or cost model.",
        ]
        return V134QCommercialAerospaceBroaderHitMildBlockAuditReport(
            summary=summary,
            compare_rows=compare_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QCommercialAerospaceBroaderHitMildBlockAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QCommercialAerospaceBroaderHitMildBlockAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134q_commercial_aerospace_broader_hit_mild_block_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
