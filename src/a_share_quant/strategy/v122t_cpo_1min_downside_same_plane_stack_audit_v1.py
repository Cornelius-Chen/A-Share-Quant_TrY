from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v122_1min_downside_stack_utils import (
    evaluate_date_split,
    evaluate_score,
    evaluate_symbol_holdout,
    load_recent_1min_rows_with_downside_stack,
)


@dataclass(slots=True)
class V122TCpo1MinDownsideSamePlaneStackAuditReport:
    summary: dict[str, Any]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


class V122TCpo1MinDownsideSamePlaneStackAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122TCpo1MinDownsideSamePlaneStackAuditReport:
        rows = load_recent_1min_rows_with_downside_stack(self.repo_root)
        base_metrics = evaluate_score(rows, score_field="downside_failure_score")
        stack_metrics = evaluate_score(rows, score_field="board_micro_risk_stack_score")
        base_time = evaluate_date_split(rows, score_field="downside_failure_score")
        stack_time = evaluate_date_split(rows, score_field="board_micro_risk_stack_score")
        base_symbol = evaluate_symbol_holdout(rows, score_field="downside_failure_score")
        stack_symbol = evaluate_symbol_holdout(rows, score_field="board_micro_risk_stack_score")

        comparison_rows = [
            {
                "score_name": "downside_failure_score",
                **base_metrics,
                **base_time,
                **base_symbol,
            },
            {
                "score_name": "board_micro_risk_stack_score",
                **stack_metrics,
                **stack_time,
                **stack_symbol,
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v122t_cpo_1min_downside_same_plane_stack_audit_v1",
            "row_count": len(rows),
            "base_discovery_gap": base_metrics["mean_gap_positive_minus_negative"],
            "stack_discovery_gap": stack_metrics["mean_gap_positive_minus_negative"],
            "base_q75_balanced_accuracy": base_metrics["balanced_accuracy_q75"],
            "stack_q75_balanced_accuracy": stack_metrics["balanced_accuracy_q75"],
            "base_time_split_mean": base_time["mean_test_balanced_accuracy"],
            "stack_time_split_mean": stack_time["mean_test_balanced_accuracy"],
            "base_symbol_holdout_mean": base_symbol["mean_test_balanced_accuracy"],
            "stack_symbol_holdout_mean": stack_symbol["mean_test_balanced_accuracy"],
            "stack_improves_over_base": (
                stack_metrics["mean_gap_positive_minus_negative"] > base_metrics["mean_gap_positive_minus_negative"]
                and stack_time["mean_test_balanced_accuracy"] >= base_time["mean_test_balanced_accuracy"]
                and stack_symbol["mean_test_balanced_accuracy"] >= base_symbol["mean_test_balanced_accuracy"]
            ),
            "recommended_next_posture": "formal_attachment_decision_stopline",
        }
        interpretation = [
            "V1.22T tests the only honest attachment posture available right now: a recent same-plane stack on the 1-minute label surface.",
            "The question is not whether the stack looks more sophisticated, but whether it materially improves over the standalone downside failure score.",
            "If the stack does not improve discovery and transfer together, attachment should be deferred.",
        ]
        return V122TCpo1MinDownsideSamePlaneStackAuditReport(
            summary=summary,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122TCpo1MinDownsideSamePlaneStackAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122TCpo1MinDownsideSamePlaneStackAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122t_cpo_1min_downside_same_plane_stack_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
