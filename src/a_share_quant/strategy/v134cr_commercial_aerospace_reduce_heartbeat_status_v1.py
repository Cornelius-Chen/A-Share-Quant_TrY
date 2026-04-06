from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CRCommercialAerospaceReduceHeartbeatStatusV1Report:
    summary: dict[str, Any]
    heartbeat_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "heartbeat_rows": self.heartbeat_rows,
            "interpretation": self.interpretation,
        }


class V134CRCommercialAerospaceReduceHeartbeatStatusV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.handoff_path = analysis_dir / "v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1.json"
        self.blocker_path = analysis_dir / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_reduce_heartbeat_status_v1.csv"

    def analyze(self) -> V134CRCommercialAerospaceReduceHeartbeatStatusV1Report:
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        blockers = json.loads(self.blocker_path.read_text(encoding="utf-8"))

        heartbeat_rows = [
            {"key": "reduce_status", "value": "frozen_mainline"},
            {"key": "broad_reduce_tuning", "value": "stopped"},
            {"key": "local_residue_policy", "value": "supervision_only"},
            {"key": "execution_blocker_count", "value": blockers["summary"]["full_reduce_binding_blocker_count"]},
            {"key": "next_frontier_state", "value": "intraday_add_deferred"},
            {"key": "next_reduce_action", "value": "do_not_reopen_without_explicit_gate_or_local_residue_need"},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(heartbeat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(heartbeat_rows)

        summary = {
            "acceptance_posture": "freeze_v134cr_commercial_aerospace_reduce_heartbeat_status_v1",
            "reduce_status": "frozen_mainline",
            "execution_blocker_count": blockers["summary"]["full_reduce_binding_blocker_count"],
            "handoff_status": handoff["summary"]["authoritative_status"],
            "heartbeat_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_heartbeat_ready_for_do_not_drift_posture",
        }
        interpretation = [
            "V1.34CR compresses the reduce branch into a minimal operational heartbeat.",
            "The point is simple: reduce is frozen, residue is local-only, execution blockers remain explicit, and the next frontier is deferred rather than silently opened.",
        ]
        return V134CRCommercialAerospaceReduceHeartbeatStatusV1Report(
            summary=summary,
            heartbeat_rows=heartbeat_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CRCommercialAerospaceReduceHeartbeatStatusV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CRCommercialAerospaceReduceHeartbeatStatusV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cr_commercial_aerospace_reduce_heartbeat_status_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
