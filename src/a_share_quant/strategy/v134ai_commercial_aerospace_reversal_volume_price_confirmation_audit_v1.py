from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import _symbol_to_archive_member


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


@dataclass(slots=True)
class V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Report:
    summary: dict[str, Any]
    feature_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_rows": self.feature_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_volume_price_confirmation_audit_v1.csv"
        )

    def _load_reversal_sessions(self) -> list[dict[str, Any]]:
        with self.horizon_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _load_first_hour_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:61]
        return [
            {
                "minute_index": idx,
                "timestamp": row[0],
                "open_px": float(row[3]),
                "close_px": float(row[4]),
                "high_px": float(row[5]),
                "low_px": float(row[6]),
                "volume": float(row[7]),
                "amount": float(row[8]),
            }
            for idx, row in enumerate(raw_rows, start=1)
        ]

    def analyze(self) -> V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Report:
        session_rows: list[dict[str, Any]] = []
        reversal_sessions = self._load_reversal_sessions()

        for row in reversal_sessions:
            trade_date = row["trade_date"]
            symbol = row["symbol"]
            minute_rows = self._load_first_hour_rows(trade_date, symbol)
            reversal_minute = int(row["reversal_minute"])
            horizon_5d = float(row["horizon_pnl_5d"]) if row["horizon_pnl_5d"] != "" else None
            if horizon_5d is None:
                continue

            total_amount_60 = sum(item["amount"] for item in minute_rows)
            total_down_amount_60 = sum(item["amount"] for item in minute_rows if item["close_px"] < item["open_px"])
            total_up_amount_60 = sum(item["amount"] for item in minute_rows if item["close_px"] > item["open_px"])
            first_5_amount = sum(item["amount"] for item in minute_rows[:5])
            first_15_amount = sum(item["amount"] for item in minute_rows[:15])
            after_reversal = minute_rows[reversal_minute:]
            post_reversal_up_amount = sum(item["amount"] for item in after_reversal if item["close_px"] > item["open_px"])
            post_reversal_total_amount = sum(item["amount"] for item in after_reversal)
            first_5_open = minute_rows[0]["open_px"]
            first_5_close = minute_rows[min(4, len(minute_rows) - 1)]["close_px"]
            first_15_close = minute_rows[min(14, len(minute_rows) - 1)]["close_px"]
            hour_close = minute_rows[-1]["close_px"]
            reversal_fill_open = minute_rows[min(reversal_minute, len(minute_rows) - 1)]["open_px"]

            regime_label = "rebound_cost_case" if horizon_5d > 0 else "followthrough_benefit_case"
            session_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "month_bucket": row["month_bucket"],
                    "reversal_minute": reversal_minute,
                    "horizon_pnl_5d": round(horizon_5d, 4),
                    "regime_label": regime_label,
                    "open_burst_return_5m": round(first_5_close / first_5_open - 1.0, 6),
                    "return_15m": round(first_15_close / first_5_open - 1.0, 6),
                    "down_amount_share_60": round(_safe_divide(total_down_amount_60, total_amount_60), 6),
                    "up_amount_share_60": round(_safe_divide(total_up_amount_60, total_amount_60), 6),
                    "burst_amount_share_5": round(_safe_divide(first_5_amount, total_amount_60), 6),
                    "burst_amount_share_15": round(_safe_divide(first_15_amount, total_amount_60), 6),
                    "post_reversal_up_amount_share": round(
                        _safe_divide(post_reversal_up_amount, post_reversal_total_amount), 6
                    ),
                    "post_reversal_close_return_to_hour_close": round(hour_close / reversal_fill_open - 1.0, 6),
                }
            )

        feature_rows: list[dict[str, Any]] = []
        for feature_name in (
            "open_burst_return_5m",
            "return_15m",
            "down_amount_share_60",
            "up_amount_share_60",
            "burst_amount_share_5",
            "burst_amount_share_15",
            "post_reversal_up_amount_share",
            "post_reversal_close_return_to_hour_close",
        ):
            rebound_values = [float(row[feature_name]) for row in session_rows if row["regime_label"] == "rebound_cost_case"]
            follow_values = [
                float(row[feature_name]) for row in session_rows if row["regime_label"] == "followthrough_benefit_case"
            ]
            feature_rows.append(
                {
                    "feature_name": feature_name,
                    "rebound_cost_case_count": len(rebound_values),
                    "followthrough_benefit_case_count": len(follow_values),
                    "rebound_cost_case_mean": round(sum(rebound_values) / len(rebound_values), 6) if rebound_values else 0.0,
                    "followthrough_benefit_case_mean": round(sum(follow_values) / len(follow_values), 6) if follow_values else 0.0,
                    "mean_gap_rebound_minus_followthrough": round(
                        (sum(rebound_values) / len(rebound_values) if rebound_values else 0.0)
                        - (sum(follow_values) / len(follow_values) if follow_values else 0.0),
                        6,
                    ),
                }
            )

        strongest_feature = max(feature_rows, key=lambda row: abs(row["mean_gap_rebound_minus_followthrough"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        summary = {
            "acceptance_posture": "freeze_v134ai_commercial_aerospace_reversal_volume_price_confirmation_audit_v1",
            "session_count": len(session_rows),
            "rebound_cost_case_count": sum(1 for row in session_rows if row["regime_label"] == "rebound_cost_case"),
            "followthrough_benefit_case_count": sum(
                1 for row in session_rows if row["regime_label"] == "followthrough_benefit_case"
            ),
            "strongest_feature": strongest_feature["feature_name"],
            "strongest_feature_gap_rebound_minus_followthrough": strongest_feature["mean_gap_rebound_minus_followthrough"],
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reversal_volume_price_confirmation_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AI adds a supervised volume-price confirmation pass on the current reversal sessions without changing execution rules.",
            "The goal is to see whether rebound-cost cases and follow-through-benefit cases separate on first-hour volume-price structure before any future rule refinement is considered.",
        ]
        return V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Report(
            summary=summary,
            feature_rows=feature_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AICommercialAerospaceReversalVolumePriceConfirmationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ai_commercial_aerospace_reversal_volume_price_confirmation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
