from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122SCpo1MinHistoricalBridgeOverlapAuditReport:
    summary: dict[str, Any]
    overlap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlap_rows": self.overlap_rows,
            "interpretation": self.interpretation,
        }


class V122SCpo1MinHistoricalBridgeOverlapAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122SCpo1MinHistoricalBridgeOverlapAuditReport:
        with (self.repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open(
            "r", encoding="utf-8"
        ) as handle:
            enriched_rows = list(csv.DictReader(handle))
        historical_reduce_dates = sorted(
            {
                str(row["signal_trade_date"])
                for row in enriched_rows
                if str(row.get("action_context")) == "reduce_vs_hold"
            }
        )

        with (self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv").open(
            "r", encoding="utf-8"
        ) as handle:
            recent_rows = list(csv.DictReader(handle))
        recent_1min_dates = sorted({str(row["trade_date"]) for row in recent_rows})

        historical_date_set = set(historical_reduce_dates)
        recent_date_set = set(recent_1min_dates)
        overlap_dates = sorted(historical_date_set & recent_date_set)

        overlap_rows = [
            {
                "surface_name": "historical_reduce_vs_hold_surface",
                "min_date": historical_reduce_dates[0] if historical_reduce_dates else None,
                "max_date": historical_reduce_dates[-1] if historical_reduce_dates else None,
                "date_count": len(historical_reduce_dates),
            },
            {
                "surface_name": "recent_1min_proxy_label_surface",
                "min_date": recent_1min_dates[0] if recent_1min_dates else None,
                "max_date": recent_1min_dates[-1] if recent_1min_dates else None,
                "date_count": len(recent_1min_dates),
            },
            {
                "surface_name": "direct_overlap",
                "min_date": overlap_dates[0] if overlap_dates else None,
                "max_date": overlap_dates[-1] if overlap_dates else None,
                "date_count": len(overlap_dates),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v122s_cpo_1min_historical_bridge_overlap_audit_v1",
            "historical_reduce_surface_min_date": historical_reduce_dates[0] if historical_reduce_dates else None,
            "historical_reduce_surface_max_date": historical_reduce_dates[-1] if historical_reduce_dates else None,
            "recent_1min_surface_min_date": recent_1min_dates[0] if recent_1min_dates else None,
            "recent_1min_surface_max_date": recent_1min_dates[-1] if recent_1min_dates else None,
            "overlap_day_count": len(overlap_dates),
            "direct_historical_bridge_allowed": bool(overlap_dates),
            "recommended_next_posture": (
                "recent_same_plane_stack_audit_only"
                if not overlap_dates
                else "historical_bridge_attachment_audit_allowed"
            ),
        }
        interpretation = [
            "V1.22S checks whether the recent 1-minute plane can be directly attached to the older historical reduce-side surface.",
            "The answer matters because a soft 1-minute downside component should not be smuggled into historical risk rules without date overlap.",
            "If overlap is zero, the only honest next step is a recent same-plane stack audit, not a fake historical attachment.",
        ]
        return V122SCpo1MinHistoricalBridgeOverlapAuditReport(
            summary=summary,
            overlap_rows=overlap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122SCpo1MinHistoricalBridgeOverlapAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122SCpo1MinHistoricalBridgeOverlapAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122s_cpo_1min_historical_bridge_overlap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
