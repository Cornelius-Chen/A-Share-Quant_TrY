from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qo_a_share_runtime_scheduler_stub_replacement_lane_audit_v1 import (
    V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QPAShareQORuntimeStubLaneDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QPAShareQORuntimeStubLaneDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QPAShareQORuntimeStubLaneDirectionTriageV1Report:
        report = V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "lane_row_count": report.summary["lane_row_count"],
            "excluded_row_count": report.summary["excluded_row_count"],
            "authoritative_status": "source_runtime_should_continue_through_the_single_stub_replacement_lane",
        }
        triage_rows = [
            {
                "component": "runtime_stub_lane",
                "direction": "continue_only_through_the_single_html_article_scheduler_stub_replacement_lane",
            },
            {
                "component": "excluded_adapters",
                "direction": "retain_social_and_reserved_official_adapters_outside_this_stub_lane",
            },
        ]
        interpretation = [
            "The remaining source-side runtime path is now best understood as a single stub-replacement lane.",
            "This keeps future work narrow and avoids reopening the excluded adapters.",
        ]
        return V134QPAShareQORuntimeStubLaneDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QPAShareQORuntimeStubLaneDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QPAShareQORuntimeStubLaneDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qp_a_share_qo_runtime_stub_lane_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
