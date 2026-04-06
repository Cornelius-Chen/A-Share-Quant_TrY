from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.replay.cost_models.materialize_a_share_replay_tradeable_context_binding_v1 import (
    MaterializeAShareReplayTradeableContextBindingV1,
)


@dataclass(slots=True)
class V134MQAShareReplayTradeableContextBindingAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MQAShareReplayTradeableContextBindingAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_replay_tradeable_context_binding_status_v1.csv"
        )

    def analyze(self) -> V134MQAShareReplayTradeableContextBindingAuditV1Report:
        materialized = MaterializeAShareReplayTradeableContextBindingV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "tradeable_context_binding",
                "component_state": (
                    "materialized_date_level_binding"
                    if summary["date_level_bound_count"] > 0
                    else "materialized_missing_coverage_surface"
                ),
                "artifact_path": summary["binding_path"],
                "coverage_note": f"date_level_bound_count = {summary['date_level_bound_count']}",
            },
            {
                "component": "binding_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"missing_date_context_count = {summary['missing_date_context_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "binding_row_count": summary["binding_row_count"],
            "date_level_bound_count": summary["date_level_bound_count"],
            "missing_date_context_count": summary["missing_date_context_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": (
                "a_share_replay_tradeable_context_date_level_binding_materialized"
                if summary["date_level_bound_count"] > 0
                else "a_share_replay_tradeable_context_missing_coverage_surface_materialized"
            ),
        }
        interpretation = [
            "Replay now has an explicit tradeable-context coverage surface instead of an unexamined assumption about market linkage.",
            "In the current repository state, the dominant outcome is still missing date coverage rather than successful date-level binding.",
        ]
        return V134MQAShareReplayTradeableContextBindingAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MQAShareReplayTradeableContextBindingAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MQAShareReplayTradeableContextBindingAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mq_a_share_replay_tradeable_context_binding_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
