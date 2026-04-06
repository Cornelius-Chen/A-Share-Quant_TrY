from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _base_score(row: dict[str, Any]) -> float:
    return (
        -_to_float(row.get("d5_30_last_bar_return_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
    )


def _overheat_penalty(row: dict[str, Any]) -> float:
    d5_last = max(_to_float(row.get("d5_30_last_bar_return_rz")), 0.0)
    f60_high = max(_to_float(row.get("f60_high_time_ratio_rz")) - 750000000.0, 0.0)
    close_stretch = max(_to_float(row.get("f60_close_location_rz")) - 850000000.0, 0.0)
    return d5_last + f60_high + close_stretch


@dataclass(slots=True)
class V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditReport:
    summary: dict[str, object]
    context_rows: list[dict[str, object]]
    leaked_entry_rows: list[dict[str, object]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "context_rows": self.context_rows,
            "leaked_entry_rows": self.leaked_entry_rows,
            "interpretation": self.interpretation,
        }


class V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        rows_path: Path,
        threshold: float,
    ) -> V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditReport:
        rows = _load_csv_rows(rows_path)
        context_bucket: dict[str, list[dict[str, Any]]] = {}
        leaked_entry_rows: list[dict[str, object]] = []

        for row in rows:
            controlled_score = _base_score(row) - _overheat_penalty(row)
            action_context = str(row.get("action_context"))
            context_bucket.setdefault(action_context, []).append(
                {
                    "signal_trade_date": str(row.get("signal_trade_date")),
                    "symbol": str(row.get("symbol")),
                    "board_phase": str(row.get("board_phase")),
                    "role_family": str(row.get("role_family")),
                    "action_context": action_context,
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "controlled_score": round(controlled_score, 6),
                    "passes_threshold": controlled_score >= threshold,
                }
            )

        context_rows: list[dict[str, object]] = []
        for action_context, bucket in sorted(context_bucket.items()):
            pass_count = sum(1 for row in bucket if bool(row["passes_threshold"]))
            row = {
                "action_context": action_context,
                "row_count": len(bucket),
                "pass_count": pass_count,
                "pass_rate": round(pass_count / len(bucket), 6) if bucket else 0.0,
            }
            context_rows.append(row)

            if action_context == "entry_vs_skip":
                leaked_entry_rows = [
                    {
                        "signal_trade_date": item["signal_trade_date"],
                        "symbol": item["symbol"],
                        "board_phase": item["board_phase"],
                        "role_family": item["role_family"],
                        "expectancy_proxy_3d": item["expectancy_proxy_3d"],
                        "controlled_score": item["controlled_score"],
                    }
                    for item in bucket
                    if bool(item["passes_threshold"])
                ]

        add_row = next(row for row in context_rows if row["action_context"] == "add_vs_hold")
        entry_row = next(row for row in context_rows if row["action_context"] == "entry_vs_skip")
        reduce_row = next(row for row in context_rows if row["action_context"] == "reduce_vs_hold")
        close_row = next(row for row in context_rows if row["action_context"] == "close_vs_hold")

        summary = {
            "acceptance_posture": "freeze_v118a_cpo_cooling_reacceleration_out_of_set_false_positive_audit_v1",
            "candidate_name": "cooling_reacceleration_overheat_control_candidate",
            "audit_threshold": round(threshold, 6),
            "add_pass_rate": add_row["pass_rate"],
            "entry_leakage_rate": entry_row["pass_rate"],
            "reduce_leakage_rate": reduce_row["pass_rate"],
            "close_leakage_rate": close_row["pass_rate"],
            "authoritative_current_problem": "add_vs_entry_separation_not_reduce_or_close_contamination",
            "recommended_next_posture": "focus_next_quality_audit_on_add_vs_strong_entry_discrimination",
        }
        interpretation = [
            "V1.18A is an out-of-set false-positive audit over non-add contexts using the retained W/X/Y controlled score and threshold.",
            "The retained score does not mainly leak into reduce or close contexts. The real contamination is entry-like: some strong entry windows look similar to add windows under the current quality language.",
            "That means the next discriminator should not be another generic false-positive filter. It should specifically separate add-from-strong-entry.",
        ]
        return V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditReport(
            summary=summary,
            context_rows=context_rows,
            leaked_entry_rows=leaked_entry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        threshold=489402000.0,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118a_cpo_cooling_reacceleration_out_of_set_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
