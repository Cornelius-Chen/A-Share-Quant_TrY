from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import _symbol_to_archive_member


@dataclass(slots=True)
class V134XCommercialAerospaceReversalLateSevereBlockAuditReport:
    summary: dict[str, Any]
    impacted_rows: list[dict[str, Any]]
    compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "impacted_rows": self.impacted_rows,
            "compare_rows": self.compare_rows,
            "interpretation": self.interpretation,
        }


class V134XCommercialAerospaceReversalLateSevereBlockAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_mild_block_sessions_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.cutoff_minute = 180
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_late_severe_block_audit_v1.csv"
        )

    def _load_close_price(self, trade_date: str, symbol: str) -> float:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        return float(rows[-1][4])

    def analyze(self) -> V134XCommercialAerospaceReversalLateSevereBlockAuditReport:
        with self.sessions_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        impacted_rows: list[dict[str, Any]] = []
        base_total = 0.0
        adjusted_total = 0.0

        for row in rows:
            same_day_loss_avoided = float(row["same_day_loss_avoided"])
            base_total += same_day_loss_avoided

            predicted_tier = row["predicted_tier"]
            first_severe_minute = int(row["first_severe_minute"]) if row["first_severe_minute"] else None
            filled_step_count = int(row["filled_step_count"])

            adjusted_same_day_loss_avoided = same_day_loss_avoided
            if (
                predicted_tier == "reversal_watch"
                and first_severe_minute is not None
                and first_severe_minute >= self.cutoff_minute
                and filled_step_count >= 2
            ):
                trade_date = row["trade_date"]
                symbol = row["symbol"]
                entry_price = float(row["entry_price"])
                close_price = self._load_close_price(trade_date, symbol)
                quantity = int(row["reference_quantity"])
                remaining_after_reversal = quantity // 2
                if remaining_after_reversal % 100 != 0:
                    remaining_after_reversal = (remaining_after_reversal // 100) * 100
                if remaining_after_reversal <= 0:
                    remaining_after_reversal = quantity - (quantity // 2)
                with (self.repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_orders_v1.csv").open(
                    "r", encoding="utf-8-sig", newline=""
                ) as handle:
                    order_rows = [
                        order for order in csv.DictReader(handle)
                        if order["trade_date"] == trade_date and order["symbol"] == symbol
                    ]
                reversal_row = next(order for order in order_rows if order["trigger_tier"] == "reversal_watch")
                reversal_pnl = float(reversal_row["pnl_after_cost"])
                hold_remainder_pnl = remaining_after_reversal * (close_price - entry_price)
                adjusted_simulated_pnl = reversal_pnl + hold_remainder_pnl
                baseline_hold_pnl = float(row["baseline_hold_pnl"])
                adjusted_same_day_loss_avoided = round(adjusted_simulated_pnl - baseline_hold_pnl, 4)
                impacted_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "predicted_tier": predicted_tier,
                        "first_severe_minute": first_severe_minute,
                        "base_same_day_loss_avoided": same_day_loss_avoided,
                        "adjusted_same_day_loss_avoided": adjusted_same_day_loss_avoided,
                        "delta": round(adjusted_same_day_loss_avoided - same_day_loss_avoided, 4),
                    }
                )

            adjusted_total += adjusted_same_day_loss_avoided

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if impacted_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(impacted_rows[0].keys()))
                writer.writeheader()
                writer.writerows(impacted_rows)

        compare_rows = [
            {
                "variant": "current_wider_reference",
                "same_day_loss_avoided_total": round(base_total, 4),
            },
            {
                "variant": "reversal_late_severe_blocked",
                "same_day_loss_avoided_total": round(adjusted_total, 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134x_commercial_aerospace_reversal_late_severe_block_audit_v1",
            "late_severe_cutoff_minute": self.cutoff_minute,
            "impacted_session_count": len(impacted_rows),
            "base_same_day_loss_avoided_total": round(base_total, 4),
            "adjusted_same_day_loss_avoided_total": round(adjusted_total, 4),
            "same_day_loss_avoided_delta": round(adjusted_total - base_total, 4),
            "impact_csv": str(self.output_csv.relative_to(self.repo_root)) if impacted_rows else "",
            "authoritative_output": "commercial_aerospace_reversal_late_severe_block_audit_ready_for_local_cluster_direction_triage",
        }
        interpretation = [
            "V1.34X audits a single local refinement on the current wider reference: block the terminal severe leg when a reversal-predicted session only reaches severe very late in the day.",
            "The goal is not another surface change; it is to test whether the only remaining negative cluster is an over-late terminal execution artifact.",
        ]
        return V134XCommercialAerospaceReversalLateSevereBlockAuditReport(
            summary=summary,
            impacted_rows=impacted_rows,
            compare_rows=compare_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134XCommercialAerospaceReversalLateSevereBlockAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134XCommercialAerospaceReversalLateSevereBlockAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134x_commercial_aerospace_reversal_late_severe_block_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
