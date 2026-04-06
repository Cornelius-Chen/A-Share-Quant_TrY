from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134LWAShareExecutionBindingBlockerStackAuditV1Report:
    summary: dict[str, Any]
    blocker_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "blocker_rows": self.blocker_rows,
            "interpretation": self.interpretation,
        }


class V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.replay_backlog_path = (
            repo_root / "data" / "reference" / "info_center" / "replay_registry" / "a_share_shadow_replay_backlog_v1.csv"
        )
        self.gate_path = (
            repo_root / "data" / "reference" / "info_center" / "governance_registry" / "a_share_promotion_gate_registry_v1.csv"
        )
        self.source_residual_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_activation_residual_backlog_v1.csv"
        )
        self.live_like_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_live_like_view_materialization_registry_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_execution_binding_blocker_stack_v1.csv"

    def analyze(self) -> V134LWAShareExecutionBindingBlockerStackAuditV1Report:
        replay_backlog_rows = _read_csv(self.replay_backlog_path)
        gate_rows = _read_csv(self.gate_path)
        source_residual_rows = _read_csv(self.source_residual_path)
        live_like_rows = _read_csv(self.live_like_path)

        blocker_rows = [
            {
                "blocker_id": "execution_authority_gate_closed",
                "blocker_layer": "governance",
                "blocker_state": "active",
                "blocking_reason": next(
                    row["gate_reason"] for row in gate_rows if row["gate_id"] == "execution_authority_gate"
                ),
            },
            {
                "blocker_id": "live_like_opening_gate_closed",
                "blocker_layer": "governance",
                "blocker_state": "active",
                "blocking_reason": next(
                    row["gate_reason"] for row in gate_rows if row["gate_id"] == "live_like_opening_gate"
                ),
            },
            {
                "blocker_id": "replay_execution_binding_backlog",
                "blocker_layer": "replay",
                "blocker_state": "active",
                "blocking_reason": next(
                    row["backlog_reason"] for row in replay_backlog_rows if row["replay_component"] == "execution_binding"
                ),
            },
            {
                "blocker_id": "replay_cost_model_backlog",
                "blocker_layer": "replay",
                "blocker_state": "active",
                "blocking_reason": next(
                    row["backlog_reason"] for row in replay_backlog_rows if row["replay_component"] == "cost_model_binding"
                ),
            },
            {
                "blocker_id": "network_fetch_binding_gap",
                "blocker_layer": "source_activation",
                "blocker_state": "active",
                "blocking_reason": next(
                    row["residual_reason"] for row in source_residual_rows if row["residual_class"] == "network_fetch_binding_gap"
                ),
            },
            {
                "blocker_id": "live_like_materialized_but_blocked",
                "blocker_layer": "serving",
                "blocker_state": "active",
                "blocking_reason": f"materialized_live_like_view_count = {sum(row['view_state'] == 'materialized_but_blocked' for row in live_like_rows)}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(blocker_rows[0].keys()))
            writer.writeheader()
            writer.writerows(blocker_rows)

        summary = {
            "blocker_count": len(blocker_rows),
            "governance_blocker_count": sum(row["blocker_layer"] == "governance" for row in blocker_rows),
            "replay_blocker_count": sum(row["blocker_layer"] == "replay" for row in blocker_rows),
            "source_blocker_count": sum(row["blocker_layer"] == "source_activation" for row in blocker_rows),
            "serving_blocker_count": sum(row["blocker_layer"] == "serving" for row in blocker_rows),
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_execution_binding_blocker_stack_explicit",
        }
        interpretation = [
            "Execution binding is no longer blocked by vague incompleteness; it is blocked by a named cross-layer stack covering governance, replay, source activation, and serving.",
            "This is the correct stopline before any promotion attempt: the remaining work is infrastructure closure, not more semantic research.",
        ]
        return V134LWAShareExecutionBindingBlockerStackAuditV1Report(
            summary=summary, blocker_rows=blocker_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LWAShareExecutionBindingBlockerStackAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lw_a_share_execution_binding_blocker_stack_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
