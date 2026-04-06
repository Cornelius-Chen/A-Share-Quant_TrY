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
class V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditReport:
    summary: dict[str, Any]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


class V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v123m_payload: dict[str, Any]) -> V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditReport:
        candidate_name = str(v123m_payload["summary"]["selected_candidate_name"])
        threshold = _to_float(v123m_payload["candidate_score_rows"][0]["best_threshold"])
        interval_start = str(v123m_payload["summary"]["residual_interval_start"])
        interval_end = str(v123m_payload["summary"]["residual_interval_end"])
        rows = list(v123m_payload["scored_rows"])

        def segment_name(trade_date: str) -> str:
            if trade_date < interval_start:
                return "pre_interval_negative"
            if interval_start <= trade_date <= interval_end:
                return "residual_interval_positive"
            return "post_interval_negative"

        boundary_rows: list[dict[str, Any]] = []
        for name in ("pre_interval_negative", "residual_interval_positive", "post_interval_negative"):
            segment_rows = [row for row in rows if segment_name(str(row["trade_date"])) == name]
            pass_count = sum(1 for row in segment_rows if _to_float(row[candidate_name]) >= threshold)
            boundary_rows.append(
                {
                    "segment_name": name,
                    "row_count": len(segment_rows),
                    "pass_count": pass_count,
                    "pass_rate": round(pass_count / len(segment_rows), 6) if segment_rows else 0.0,
                    "mean_score": round(
                        sum(_to_float(row[candidate_name]) for row in segment_rows) / len(segment_rows), 6
                    )
                    if segment_rows
                    else 0.0,
                }
            )

        pre_pass_rate = next(row["pass_rate"] for row in boundary_rows if row["segment_name"] == "pre_interval_negative")
        post_pass_rate = next(row["pass_rate"] for row in boundary_rows if row["segment_name"] == "post_interval_negative")
        positive_pass_rate = next(
            row["pass_rate"] for row in boundary_rows if row["segment_name"] == "residual_interval_positive"
        )
        summary = {
            "acceptance_posture": "freeze_v123o_cpo_daily_residual_downside_boundary_false_positive_audit_v1",
            "candidate_name": candidate_name,
            "threshold": round(threshold, 6),
            "positive_pass_rate": positive_pass_rate,
            "pre_interval_false_positive_rate": pre_pass_rate,
            "post_interval_false_positive_rate": post_pass_rate,
            "boundary_false_positive_posture": (
                "contained"
                if max(pre_pass_rate, post_pass_rate) < positive_pass_rate
                else "too_wide_across_interval_boundary"
            ),
            "recommended_next_posture": "triage_residual_downside_branch",
        }
        interpretation = [
            "V1.23O checks whether the residual downside line only lights up inside the true residual drawdown interval or whether it leaks equally into the pre/post boundary negatives.",
            "This matters because the residual branch should not just be a generic weakness detector over the entire held-pair regime.",
            "A useful residual downside line should still separate the true drawdown core from the nearby pre- and post-interval negatives.",
        ]
        return V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditReport(
            summary=summary,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditAnalyzer(repo_root=repo_root)
    v123m_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    result = analyzer.analyze(v123m_payload=v123m_payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123o_cpo_daily_residual_downside_boundary_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
