from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_change_action_surface_v1 import (
    MaterializeAShareInternalHotNewsProgramChangeActionSurfaceV1,
)


@dataclass(slots=True)
class V134SKAShareInternalHotNewsProgramChangeActionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SKAShareInternalHotNewsProgramChangeActionAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramChangeActionSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "change_action_surface",
                "component_state": "read_ready_internal_only",
                "metric": "action_row_count",
                "value": str(materialized.summary["action_row_count"]),
            },
            {
                "component": "top_risk_action",
                "component_state": "materialized",
                "metric": "top_risk_action",
                "value": materialized.summary["top_risk_action"],
            },
            {
                "component": "top_opportunity_action",
                "component_state": "materialized",
                "metric": "top_opportunity_action",
                "value": materialized.summary["top_opportunity_action"],
            },
            {
                "component": "global_program_action_mode",
                "component_state": "materialized",
                "metric": "global_program_action_mode",
                "value": materialized.summary["global_program_action_mode"],
            },
            {
                "component": "session_action_gate",
                "component_state": "materialized",
                "metric": "session_action_gate",
                "value": materialized.summary["session_action_gate"],
            },
        ]
        interpretation = [
            "The program now receives action hints above the raw change signal.",
            "This layer translates stable or shifting snapshot states into explicit handling suggestions for the downstream consumer, with session-aware gating.",
        ]
        return V134SKAShareInternalHotNewsProgramChangeActionAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SKAShareInternalHotNewsProgramChangeActionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sk_a_share_internal_hot_news_program_change_action_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
