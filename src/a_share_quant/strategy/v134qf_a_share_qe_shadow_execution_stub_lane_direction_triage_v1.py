from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qe_a_share_shadow_execution_stub_replacement_lane_audit_v1 import (
    V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Report:
        report = V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "stub_row_count": report.summary["stub_row_count"],
            "lane_overlay_row_count": report.summary["lane_overlay_row_count"],
            "excluded_boundary_count": report.summary["excluded_boundary_count"],
            "authoritative_status": "shadow_execution_stub_replacement_lane_is_ready_for_internal_replay_progress_but_not_for_global_stub_replacement",
        }
        triage_rows = [
            {
                "component": "stub_replacement_lane",
                "direction": "retain_as_the_internal_replay_progress_lane_for_the_15_overlay_rows",
            },
            {
                "component": "base_stub_registry",
                "direction": "keep_base_stub_unchanged_until_a_later_explicit_promotion_decision_exists",
            },
            {
                "component": "boundary_exclusions",
                "direction": "retain_the_2_external_boundary_rows_outside_the_replacement_lane_and_do_not_force_them_into_the_stub_replacement_scope",
            },
        ]
        interpretation = [
            "The replacement lane is now explicit enough to guide further replay-internal progress without pretending that the base stub has already been globally replaced.",
            "That keeps the boundary between shadow-only improvement and execution-facing promotion clean.",
        ]
        return V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qf_a_share_qe_shadow_execution_stub_lane_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
