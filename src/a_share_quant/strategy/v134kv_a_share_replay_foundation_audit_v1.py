from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.replay.shadow.materialize_a_share_replay_foundation_v1 import (
    MaterializeAShareReplayFoundationV1,
)


@dataclass(slots=True)
class V134KVAShareReplayFoundationAuditV1Report:
    summary: dict[str, Any]
    replay_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "replay_rows": self.replay_rows,
            "interpretation": self.interpretation,
        }


class V134KVAShareReplayFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_replay_foundation_status_v1.csv"

    def analyze(self) -> V134KVAShareReplayFoundationAuditV1Report:
        materialized = MaterializeAShareReplayFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        replay_rows = [
            {
                "replay_component": "shadow_surface",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["shadow_surface_path"],
                "coverage_note": f"shadow_surface_row_count = {summary['shadow_surface_row_count']}",
            },
            {
                "replay_component": "shadow_lane_registry",
                "component_state": "materialized_read_only_lane",
                "artifact_path": summary["lane_registry_path"],
                "coverage_note": f"shadow_context_ready_count = {summary['shadow_context_ready_count']}",
            },
            {
                "replay_component": "shadow_replay_backlog",
                "component_state": "backlog_materialized_not_bound_to_execution",
                "artifact_path": summary["backlog_path"],
                "coverage_note": f"blocked_count = {summary['blocked_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(replay_rows[0].keys()))
            writer.writeheader()
            writer.writerows(replay_rows)

        report_summary = {
            "acceptance_posture": "build_v134kv_a_share_replay_foundation_audit_v1",
            "shadow_surface_row_count": summary["shadow_surface_row_count"],
            "shadow_context_ready_count": summary["shadow_context_ready_count"],
            "intraday_only_watch_count": summary["intraday_only_watch_count"],
            "blocked_count": summary["blocked_count"],
            "replay_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KV creates the first read-only shadow replay surface by binding PTI time slices to market coverage status.",
            "The result is intentionally non-promotive: it is a lawful replay view, not an execution surface, and it preserves market-context gaps instead of faking them away.",
        ]
        return V134KVAShareReplayFoundationAuditV1Report(
            summary=report_summary,
            replay_rows=replay_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134KVAShareReplayFoundationAuditV1Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KVAShareReplayFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kv_a_share_replay_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
