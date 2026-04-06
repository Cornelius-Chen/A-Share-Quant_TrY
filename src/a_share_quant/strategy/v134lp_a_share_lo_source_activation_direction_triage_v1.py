from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lo_a_share_source_activation_foundation_audit_v1 import (
    V134LOAShareSourceActivationFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LPAShareLOSourceActivationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LPAShareLOSourceActivationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LPAShareLOSourceActivationDirectionTriageV1Report:
        audit = V134LOAShareSourceActivationFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "local_file_feeds",
                "direction": "freeze_as_current_real_ingest_base",
            },
            {
                "component": "url_catalog_sources",
                "direction": "retain_as_catalogued_sources_pending_live_fetch_adapters",
            },
            {
                "component": "placeholder_sources",
                "direction": "retain_for_future_locator_binding_or retirement",
            },
            {
                "component": "next_frontier",
                "direction": "shift_later_into_selective_live_fetch_adapter_activation_and real_scheduler_binding",
            },
        ]
        summary = {
            "active_local_ingest_count": audit.summary["active_local_ingest_count"],
            "historical_url_catalog_count": audit.summary["historical_url_catalog_count"],
            "locally_activatable_job_count": audit.summary["locally_activatable_job_count"],
            "authoritative_status": "source_activation_complete_enough_to_freeze_as_local_real_ingest_base",
        }
        interpretation = [
            "Source activation is now real where the repo already owns files, and honest where it does not.",
            "Future progress should add live fetch adapters selectively rather than pretending the historical URL catalog is already a stable real-time intake layer.",
        ]
        return V134LPAShareLOSourceActivationDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LPAShareLOSourceActivationDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LPAShareLOSourceActivationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lp_a_share_lo_source_activation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
