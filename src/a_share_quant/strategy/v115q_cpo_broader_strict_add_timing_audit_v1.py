from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115o_cpo_intraday_strict_band_signal_timing_audit_v1 import (
    V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer,
    V115OCpoIntradayStrictBandSignalTimingAuditReport,
    write_csv_rows as write_timing_csv_rows,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V115QCpoBroaderStrictAddTimingAuditReport:
    summary: dict[str, Any]
    timing_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "timing_rows": self.timing_rows,
            "checkpoint_rows": self.checkpoint_rows,
            "interpretation": self.interpretation,
        }


class V115QCpoBroaderStrictAddTimingAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V115QCpoBroaderStrictAddTimingAuditReport:
        base_rows = _load_rows(
            self.repo_root / "data" / "training" / "cpo_intraday_strict_band_overlay_audit_rows_v1.csv"
        )
        strict_add_rows = [
            row
            for row in base_rows
            if str(row.get("is_strict_candidate_add_band")) == "True"
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        training_view_rows = _load_rows(
            self.repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv"
        )
        feature_base_rows = _load_rows(
            self.repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv"
        )
        timing_report: V115OCpoIntradayStrictBandSignalTimingAuditReport = (
            V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer(repo_root=self.repo_root).analyze(
                strict_overlay_rows=strict_add_rows,
                training_view_rows=training_view_rows,
                feature_base_rows=feature_base_rows,
            )
        )

        enriched_rows: list[dict[str, Any]] = []
        by_key = {
            (str(row["signal_trade_date"]), str(row["symbol"])): row for row in strict_add_rows
        }
        for row in timing_report.timing_rows:
            extra = by_key[(str(row["signal_trade_date"]), str(row["symbol"]))]
            enriched_rows.append(
                {
                    **row,
                    "expectancy_proxy_3d": round(_to_float(extra.get("expectancy_proxy_3d")), 6),
                    "max_adverse_return_3d": round(_to_float(extra.get("max_adverse_return_3d")), 6),
                    "forward_close_return_3d": round(_to_float(extra.get("forward_close_return_3d")), 6),
                    "action_favored_3d": str(extra.get("action_favored_3d")) == "True",
                    "state_band": str(extra.get("state_band")),
                }
            )

        same_session_rows = [row for row in enriched_rows if str(row["timing_bucket"]) == "intraday_same_session"]
        positive_rows = [row for row in enriched_rows if _to_float(row.get("expectancy_proxy_3d")) > 0]
        favored_rows = [row for row in enriched_rows if bool(row.get("action_favored_3d"))]
        positive_and_favored_rows = [
            row for row in enriched_rows if _to_float(row.get("expectancy_proxy_3d")) > 0 and bool(row.get("action_favored_3d"))
        ]

        summary = {
            "acceptance_posture": "freeze_v115q_cpo_broader_strict_add_timing_audit_v1",
            "strict_add_context_row_count": len(enriched_rows),
            "intraday_same_session_count": len(same_session_rows),
            "late_session_count": sum(str(row["timing_bucket"]) == "late_session" for row in enriched_rows),
            "post_close_or_next_day_count": sum(
                str(row["timing_bucket"]) == "post_close_or_next_day" for row in enriched_rows
            ),
            "unresolved_count": sum(str(row["timing_bucket"]) == "unresolved" for row in enriched_rows),
            "positive_expectancy_count": len(positive_rows),
            "action_favored_count": len(favored_rows),
            "positive_and_favored_count": len(positive_and_favored_rows),
            "positive_same_session_count": sum(
                str(row["timing_bucket"]) == "intraday_same_session" and _to_float(row.get("expectancy_proxy_3d")) > 0
                for row in enriched_rows
            ),
            "favored_same_session_count": sum(
                str(row["timing_bucket"]) == "intraday_same_session" and bool(row.get("action_favored_3d"))
                for row in enriched_rows
            ),
            "recommended_next_posture": "compare_broader_timing_aware_overlay_filters_before_any_intraday_promotion",
        }
        interpretation = [
            "V1.15Q widens timing audit from the repaired top-miss subset to all strict add_vs_hold rows, while keeping the same high-dimensional intraday visibility test.",
            "This answers whether timing-aware execution semantics survive outside the original miss-day slice before the project binds broader intraday overlays into replay.",
            "The output is still candidate-only and should feed filtered replay comparisons rather than direct promotion.",
        ]
        return V115QCpoBroaderStrictAddTimingAuditReport(
            summary=summary,
            timing_rows=enriched_rows,
            checkpoint_rows=timing_report.checkpoint_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V115QCpoBroaderStrictAddTimingAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115QCpoBroaderStrictAddTimingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    write_timing_csv_rows(
        path=repo_root / "data" / "training" / "cpo_broader_strict_add_timing_rows_v1.csv",
        rows=result.timing_rows,
    )
    write_timing_csv_rows(
        path=repo_root / "data" / "training" / "cpo_broader_strict_add_timing_checkpoints_v1.csv",
        rows=result.checkpoint_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115q_cpo_broader_strict_add_timing_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
