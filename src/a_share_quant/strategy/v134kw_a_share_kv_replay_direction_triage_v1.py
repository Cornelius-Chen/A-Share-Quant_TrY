from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kv_a_share_replay_foundation_audit_v1 import (
    V134KVAShareReplayFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KWAShareKVReplayDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KWAShareKVReplayDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KWAShareKVReplayDirectionTriageV1Report:
        audit = V134KVAShareReplayFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "replay_component": "shadow_surface",
                "direction": "freeze_as_bootstrap_read_only_replay_surface",
            },
            {
                "replay_component": "shadow_lane_registry",
                "direction": "retain_as_non_promotive_lane_until_serving_and_governance_bindings_exist",
            },
            {
                "replay_component": "next_frontier",
                "direction": "shift_into_serving_workstream_using_identity_events_market_features_pti_and_replay_as_inputs",
            },
        ]
        summary = {
            "shadow_surface_row_count": audit.summary["shadow_surface_row_count"],
            "shadow_context_ready_count": audit.summary["shadow_context_ready_count"],
            "blocked_count": audit.summary["blocked_count"],
            "authoritative_status": (
                "replay_workstream_complete_enough_to_freeze_as_read_only_shadow_and_shift_into_serving"
            ),
        }
        interpretation = [
            "Replay is now alive enough to serve as a read-only shadow lane, but it is still intentionally non-promotive.",
            "The correct next move is serving, not execution, because replay still carries explicit market-context and execution-binding backlogs.",
        ]
        return V134KWAShareKVReplayDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134KWAShareKVReplayDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KWAShareKVReplayDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kw_a_share_kv_replay_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
