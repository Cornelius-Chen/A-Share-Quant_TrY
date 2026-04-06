from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.replay.cost_models.materialize_a_share_replay_cost_model_foundation_v1 import (
    MaterializeAShareReplayCostModelFoundationV1,
)


@dataclass(slots=True)
class V134MOAShareReplayCostModelFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MOAShareReplayCostModelFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_replay_cost_model_foundation_status_v1.csv"

    def analyze(self) -> V134MOAShareReplayCostModelFoundationAuditV1Report:
        materialized = MaterializeAShareReplayCostModelFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "cost_model_registry",
                "component_state": "materialized_foundation_stub",
                "artifact_path": summary["cost_model_path"],
                "coverage_note": f"cost_model_count = {summary['cost_model_count']}",
            },
            {
                "component": "shadow_execution_journal",
                "component_state": "materialized_stub_surface",
                "artifact_path": summary["execution_journal_path"],
                "coverage_note": f"execution_journal_stub_count = {summary['execution_journal_stub_count']}",
            },
            {
                "component": "cost_model_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"limit_hit_count = {summary['limit_hit_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "cost_model_count": summary["cost_model_count"],
            "execution_journal_stub_count": summary["execution_journal_stub_count"],
            "limit_hit_count": summary["limit_hit_count"],
            "halt_or_suspend_count": summary["halt_or_suspend_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_cost_model_foundation_materialized",
        }
        interpretation = [
            "Replay cost modeling is no longer entirely deferred: the first registry and stub execution journal now exist.",
            "This reduces replay-side ambiguity even though lawful execution binding remains blocked.",
        ]
        return V134MOAShareReplayCostModelFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MOAShareReplayCostModelFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MOAShareReplayCostModelFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mo_a_share_replay_cost_model_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
