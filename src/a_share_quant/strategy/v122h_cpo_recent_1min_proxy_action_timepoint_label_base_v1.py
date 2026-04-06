from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


HORIZON = 5


@dataclass(slots=True)
class V122HCpoRecent1MinProxyActionTimepointLabelBaseReport:
    summary: dict[str, Any]
    label_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_rows": self.label_rows,
            "interpretation": self.interpretation,
        }


class V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122HCpoRecent1MinProxyActionTimepointLabelBaseReport:
        feature_table = self.repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
        with feature_table.open("r", encoding="utf-8") as handle:
            base_rows = list(csv.DictReader(handle))

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in base_rows:
            grouped.setdefault((row["symbol"], row["trade_date"]), []).append(row)

        output_path = self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "symbol",
            "trade_date",
            "bar_time",
            "clock_time",
            "proxy_action_label",
            "forward_return_5",
            "max_favorable_return_5",
            "max_adverse_return_5",
            "push_efficiency",
            "close_vs_vwap",
            "close_location",
            "late_session_integrity_score",
            "burst_then_fade_score",
            "reclaim_after_break_score",
        ]

        label_counts: dict[str, int] = {
            "add_probe": 0,
            "reduce_probe": 0,
            "close_probe": 0,
            "hold_probe": 0,
        }
        label_rows: list[dict[str, Any]] = []

        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for (_symbol, _trade_date), rows in grouped.items():
                for index in range(len(rows) - HORIZON):
                    row = rows[index]
                    current_close = float(row["close"])
                    future_rows = rows[index + 1 : index + HORIZON + 1]
                    future_close = float(future_rows[-1]["close"])
                    future_high = max(float(item["high"]) for item in future_rows)
                    future_low = min(float(item["low"]) for item in future_rows)

                    forward_return = future_close / current_close - 1.0
                    max_favorable = future_high / current_close - 1.0
                    max_adverse = future_low / current_close - 1.0

                    push_efficiency = float(row["push_efficiency"])
                    close_vs_vwap = float(row["close_vs_vwap"])
                    close_location = float(row["close_location"])
                    late_session_integrity = float(row["late_session_integrity_score"])
                    burst_then_fade = float(row["burst_then_fade_score"])
                    reclaim_after_break = float(row["reclaim_after_break_score"])

                    if (
                        forward_return > 0.0025
                        and max_adverse > -0.0035
                        and push_efficiency > 0.25
                        and close_location > 0.55
                    ):
                        label = "add_probe"
                    elif (
                        forward_return < -0.0035
                        and max_favorable < 0.0015
                        and burst_then_fade > 0.0008
                    ):
                        label = "close_probe"
                    elif (
                        max_adverse < -0.005
                        and (forward_return <= 0.0 or late_session_integrity < -0.02)
                    ):
                        label = "reduce_probe"
                    else:
                        label = "hold_probe"

                    output_row = {
                        "symbol": row["symbol"],
                        "trade_date": row["trade_date"],
                        "bar_time": row["bar_time"],
                        "clock_time": row["clock_time"],
                        "proxy_action_label": label,
                        "forward_return_5": round(forward_return, 8),
                        "max_favorable_return_5": round(max_favorable, 8),
                        "max_adverse_return_5": round(max_adverse, 8),
                        "push_efficiency": round(push_efficiency, 8),
                        "close_vs_vwap": round(close_vs_vwap, 8),
                        "close_location": round(close_location, 8),
                        "late_session_integrity_score": round(late_session_integrity, 8),
                        "burst_then_fade_score": round(burst_then_fade, 8),
                        "reclaim_after_break_score": round(reclaim_after_break, 8),
                    }
                    writer.writerow(output_row)
                    label_rows.append(output_row)
                    label_counts[label] += 1

        summary = {
            "acceptance_posture": "freeze_v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1",
            "row_count": len(label_rows),
            "horizon_bars": HORIZON,
            "label_counts": label_counts,
            "output_path": str(output_path.relative_to(self.repo_root)),
            "recommended_next_posture": "audit_candidate_families_against_proxy_action_labels",
        }
        interpretation = [
            "V1.22H creates a strict proxy action-timepoint label base on the recent 1-minute plane instead of continuing unlabeled family discovery.",
            "These are still proxy labels, not production action truth, but they are stricter and more actionable than pooled forward-return checks alone.",
            "The next step is to re-audit surviving 1-minute families against this label base rather than inventing more scores first.",
        ]
        return V122HCpoRecent1MinProxyActionTimepointLabelBaseReport(
            summary=summary,
            label_rows=[
                {"label": label, "count": count, "rate": round(count / len(label_rows), 8) if label_rows else 0.0}
                for label, count in label_counts.items()
            ],
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122HCpoRecent1MinProxyActionTimepointLabelBaseReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
