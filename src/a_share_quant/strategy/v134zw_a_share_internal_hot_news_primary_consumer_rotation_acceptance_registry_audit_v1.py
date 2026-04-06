from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1 import (
    MaterializeAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1,
)


@dataclass(slots=True)
class V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1(self.repo_root).materialize()
        rows = [
            {"component": "rotation_acceptance", "component_state": "materialized", "metric": "acceptance_state", "value": materialized.summary["acceptance_state"]},
            {"component": "rotation_acceptance", "component_state": "materialized", "metric": "accepted_top_opportunity_theme", "value": materialized.summary["accepted_top_opportunity_theme"]},
            {"component": "rotation_acceptance", "component_state": "materialized", "metric": "accepted_top_watch_symbol", "value": materialized.summary["accepted_top_watch_symbol"]},
        ]
        interpretation = [
            "This registry is the explicit manual acceptance record for the primary consumer rotation.",
            "Downstream primary snapshot and control consumers should only rotate after this registry exists in accepted state.",
        ]
        return V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zw_a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
