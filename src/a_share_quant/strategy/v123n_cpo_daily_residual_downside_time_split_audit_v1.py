from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v123_daily_residual_downside_utils import chronological_split_rows


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123NCpoDailyResidualDownsideTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V123NCpoDailyResidualDownsideTimeSplitAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v123m_payload: dict[str, Any]) -> V123NCpoDailyResidualDownsideTimeSplitAuditReport:
        candidate_name = str(v123m_payload["summary"]["selected_candidate_name"])
        scored_rows = list(v123m_payload["scored_rows"])
        split_rows = chronological_split_rows(rows=scored_rows, score_field=candidate_name)
        mean_test = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        summary = {
            "acceptance_posture": "freeze_v123n_cpo_daily_residual_downside_time_split_audit_v1",
            "candidate_name": candidate_name,
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test, 6),
            "min_test_balanced_accuracy": round(min_test, 6),
            "chronology_posture": "candidate_survives_time_split" if min_test >= 0.5 else "candidate_unstable_under_time_split",
            "recommended_next_posture": "boundary_false_positive_audit_before_any_triage",
        }
        interpretation = [
            "V1.23N checks whether the residual downside line is just a static interval marker or whether it survives chronology splits.",
            "This matters because the residual branch is built from a single problematic drawdown family and can easily overfit interval shape.",
            "Only a line that stays above random under chronological splits deserves triage budget.",
        ]
        return V123NCpoDailyResidualDownsideTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123NCpoDailyResidualDownsideTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123NCpoDailyResidualDownsideTimeSplitAuditAnalyzer(repo_root=repo_root)
    v123m_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    result = analyzer.analyze(v123m_payload=v123m_payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123n_cpo_daily_residual_downside_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
