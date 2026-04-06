from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_signal_enrichment_v1 import (
    MaterializeAShareInternalHotNewsSignalEnrichmentV1,
)


@dataclass(slots=True)
class V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsSignalEnrichmentV1(self.repo_root).materialize()
        rows = [
            {
                "component": "board_signal_enriched",
                "component_state": "materialized",
                "metric": "board_signal_row_count",
                "value": str(materialized.summary["board_signal_row_count"]),
            },
            {
                "component": "important_queue_enriched",
                "component_state": "materialized",
                "metric": "important_queue_row_count",
                "value": str(materialized.summary["important_queue_row_count"]),
            },
            {
                "component": "curated_mapping_status",
                "component_state": "measured",
                "metric": "curated_match_count",
                "value": str(materialized.summary["curated_match_count"]),
            },
            {
                "component": "mapping_status",
                "component_state": "measured",
                "metric": "missing_surface_count",
                "value": str(materialized.summary["missing_surface_count"]),
            },
        ]
        interpretation = [
            "Board and important trading signals now carry explicit beneficiary-mapping status instead of leaving blank symbol lists unexplained.",
            "Curated theme beneficiaries are applied first when the local securities pool has a credible proxy list for the detected theme.",
            "The trading layer can distinguish broad-market guidance, successfully matched board signals, and theme hits that still lack a member surface.",
        ]
        return V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ri_a_share_internal_hot_news_signal_enrichment_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
