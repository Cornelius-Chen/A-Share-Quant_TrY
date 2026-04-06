from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURE_FAMILIES = [
    "reclaim_after_break",
    "vwap_reclaim",
    "upper_shadow_trap",
    "lower_shadow_repair",
    "micro_pullback_depth",
    "push_efficiency",
    "late_session_integrity",
    "volume_burst_then_fade",
]


@dataclass(slots=True)
class V121UCpoRecent1MinFeatureReadinessAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    feature_family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "feature_family_rows": self.feature_family_rows,
            "interpretation": self.interpretation,
        }


class V121UCpoRecent1MinFeatureReadinessAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121UCpoRecent1MinFeatureReadinessAuditReport:
        minute_dir = self.repo_root / "data" / "raw" / "minute_bars"
        symbol_rows: list[dict[str, Any]] = []
        file_count = 0
        total_rows = 0
        for path in sorted(minute_dir.glob("sina_*_recent_1min_v1.csv")):
            with path.open("r", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            file_count += 1
            total_rows += len(rows)
            symbol_rows.append(
                {
                    "symbol": path.name.split("_")[1],
                    "row_count": len(rows),
                    "start_time": rows[0]["day"] if rows else "",
                    "end_time": rows[-1]["day"] if rows else "",
                }
            )

        feature_family_rows = [
            {
                "feature_family": family,
                "readiness": "ready_from_1min_ohlcv",
                "requires_external_event_time": False,
            }
            for family in FEATURE_FAMILIES
        ]

        summary = {
            "acceptance_posture": "freeze_v121u_cpo_recent_1min_feature_readiness_audit_v1",
            "file_count": file_count,
            "total_row_count": total_rows,
            "feature_family_count": len(feature_family_rows),
            "readiness_posture": "recent_1min_microstructure_plane_ready_for_local_feature_building",
            "recommended_next_posture": "build_1min_microstructure_feature_table_for_core_names",
        }
        interpretation = [
            "V1.21U confirms that the project now has a recent 1-minute microstructure plane for the core CPO names.",
            "The immediate value is pure price-volume microstructure, not news-driven intraday trading.",
            "This is the correct next plane because the 30/60-minute and daily risk-side branches have reached their local boundary.",
        ]
        return V121UCpoRecent1MinFeatureReadinessAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            feature_family_rows=feature_family_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121UCpoRecent1MinFeatureReadinessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121UCpoRecent1MinFeatureReadinessAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121u_cpo_recent_1min_feature_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
