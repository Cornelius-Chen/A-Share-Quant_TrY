from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114GMultiBoardAutonomousResearchQueueSeedReport:
    summary: dict[str, Any]
    queue_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "queue_rows": self.queue_rows,
            "interpretation": self.interpretation,
        }


class V114GMultiBoardAutonomousResearchQueueSeedAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114f_payload: dict[str, Any],
        board_queue: list[str],
    ) -> V114GMultiBoardAutonomousResearchQueueSeedReport:
        summary_f = dict(v114f_payload.get("summary", {}))
        if str(summary_f.get("acceptance_posture")) != "freeze_v114f_multi_board_autonomous_research_orchestrator_protocol_v1":
            raise ValueError("V1.14G expects V1.14F orchestrator protocol first.")

        queue_rows = []
        for order, board_name in enumerate(board_queue, start=1):
            queue_rows.append(
                {
                    "queue_order": order,
                    "board_name": board_name,
                    "queue_status": "queued",
                    "next_phase": "board_world_model",
                    "run_until": "terminal_status_or_hard_stop",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v114g_multi_board_autonomous_research_queue_seed_v1",
            "board_queue_count": len(queue_rows),
            "autonomous_queue_ready": len(queue_rows) > 0,
            "recommended_next_posture": "start_autonomous_board_worker_from_queue_head",
        }
        interpretation = [
            "V1.14G seeds the first board queue under the V1.14F bounded autonomous research protocol.",
            "Each queued board is expected to run through the full research stack without a new user prompt until it reaches terminal status or a hard stop.",
            "The queue is deliberately explicit so the orchestrator can be audited and extended board by board without losing run order.",
        ]
        return V114GMultiBoardAutonomousResearchQueueSeedReport(
            summary=summary,
            queue_rows=queue_rows,
            interpretation=interpretation,
        )


def write_v114g_multi_board_autonomous_research_queue_seed_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114GMultiBoardAutonomousResearchQueueSeedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

