from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123SCpoDailyResidualGranularBoundaryAuditReport:
    summary: dict[str, Any]
    segment_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "segment_rows": self.segment_rows,
            "interpretation": self.interpretation,
        }


class V123SCpoDailyResidualGranularBoundaryAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v123m_payload: dict[str, Any], v123r_payload: dict[str, Any]) -> V123SCpoDailyResidualGranularBoundaryAuditReport:
        candidate_name = str(v123m_payload["summary"]["selected_candidate_name"])
        threshold = _to_float(v123m_payload["candidate_score_rows"][0]["best_threshold"])
        interval_start = str(v123m_payload["summary"]["residual_interval_start"])
        interval_end = str(v123m_payload["summary"]["residual_interval_end"])
        core_map = {str(row["trade_date"]): bool(row["core_stress_label"]) for row in v123r_payload["core_rows"]}
        segment_rows = []
        for name in ("pre_interval_negative", "positive_fringe", "positive_core", "post_interval_negative"):
            if name == "pre_interval_negative":
                rows = [row for row in v123m_payload["scored_rows"] if str(row["trade_date"]) < interval_start]
            elif name == "post_interval_negative":
                rows = [row for row in v123m_payload["scored_rows"] if str(row["trade_date"]) > interval_end]
            elif name == "positive_core":
                rows = [
                    row
                    for row in v123m_payload["scored_rows"]
                    if interval_start <= str(row["trade_date"]) <= interval_end and core_map.get(str(row["trade_date"]), False)
                ]
            else:
                rows = [
                    row
                    for row in v123m_payload["scored_rows"]
                    if interval_start <= str(row["trade_date"]) <= interval_end and not core_map.get(str(row["trade_date"]), False)
                ]
            pass_count = sum(1 for row in rows if _to_float(row[candidate_name]) >= threshold)
            segment_rows.append(
                {
                    "segment_name": name,
                    "row_count": len(rows),
                    "pass_count": pass_count,
                    "pass_rate": round(pass_count / len(rows), 6) if rows else 0.0,
                    "mean_score": round(sum(_to_float(row[candidate_name]) for row in rows) / len(rows), 6) if rows else 0.0,
                }
            )

        pre_rate = next(row["pass_rate"] for row in segment_rows if row["segment_name"] == "pre_interval_negative")
        fringe_rate = next(row["pass_rate"] for row in segment_rows if row["segment_name"] == "positive_fringe")
        core_rate = next(row["pass_rate"] for row in segment_rows if row["segment_name"] == "positive_core")
        post_rate = next(row["pass_rate"] for row in segment_rows if row["segment_name"] == "post_interval_negative")
        summary = {
            "acceptance_posture": "freeze_v123s_cpo_daily_residual_granular_boundary_audit_v1",
            "candidate_name": candidate_name,
            "threshold": round(threshold, 6),
            "core_pass_rate": core_rate,
            "fringe_pass_rate": fringe_rate,
            "pre_interval_false_positive_rate": pre_rate,
            "post_interval_false_positive_rate": post_rate,
            "granular_boundary_posture": (
                "core_focused_boundary_separation"
                if core_rate > fringe_rate and fringe_rate > pre_rate and core_rate > post_rate
                else "core_and_boundary_not_cleanly_ordered"
            ),
            "recommended_next_posture": "triage_after_core_and_granular_boundary_check",
        }
        interpretation = [
            "V1.23S sharpens the earlier boundary audit by splitting the positive interval into core and fringe stress days.",
            "The question is whether the residual downside line is strongest where the drawdown is deepest, while staying relatively quieter before and after the interval.",
            "This is still a non-replay structural audit, not execution logic.",
        ]
        return V123SCpoDailyResidualGranularBoundaryAuditReport(
            summary=summary,
            segment_rows=segment_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123SCpoDailyResidualGranularBoundaryAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    v123m_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    v123r_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123r_cpo_daily_residual_core_stress_audit_v1.json").read_text(
            encoding="utf-8"
        )
    )
    analyzer = V123SCpoDailyResidualGranularBoundaryAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v123m_payload=v123m_payload, v123r_payload=v123r_payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123s_cpo_daily_residual_granular_boundary_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
