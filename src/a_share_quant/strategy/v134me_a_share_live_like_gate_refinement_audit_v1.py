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
class V134MEAShareLiveLikeGateRefinementAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MEAShareLiveLikeGateRefinementAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.gate_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "governance_registry"
            / "a_share_promotion_gate_registry_v1.csv"
        )
        self.review_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_review_activation_registry_v1.csv"
        )
        self.source_activation_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_activation_registry_v1.csv"
        )
        self.network_policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_activation_policy_v1.csv"
        )
        self.serving_live_like_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_live_like_view_materialization_registry_v1.csv"
        )
        self.replay_backlog_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_replay_backlog_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_live_like_gate_refinement_status_v1.csv"

    def analyze(self) -> V134MEAShareLiveLikeGateRefinementAuditV1Report:
        gate_rows = _read_csv(self.gate_path)
        review_rows = _read_csv(self.review_path)
        source_rows = _read_csv(self.source_activation_path)
        network_policy_rows = _read_csv(self.network_policy_path)
        live_like_rows = _read_csv(self.serving_live_like_path)
        replay_backlog_rows = _read_csv(self.replay_backlog_path)

        active_local_ingest_count = sum(row["activation_state"] == "active_local_ingest" for row in source_rows)
        policy_bound_adapter_count = sum(
            row["activation_state"] == "policy_bound_not_activated" for row in network_policy_rows
        )
        closed_gate_count = sum(row["gate_state"] == "closed" for row in gate_rows)
        active_review_queue_count = sum(row["queue_state"] == "active_bootstrap" for row in review_rows)
        materialized_but_blocked_count = sum(row["view_state"] == "materialized_but_blocked" for row in live_like_rows)
        replay_execution_backlog = any(
            row["replay_component"] == "execution_binding" for row in replay_backlog_rows
        )

        rows = [
            {
                "gate_component": "source_activation",
                "component_state": "policy_bound_not_activated",
                "supporting_count": policy_bound_adapter_count,
                "blocker": "selective_activation_shift_required",
            },
            {
                "gate_component": "review_layer",
                "component_state": "ready_bootstrap",
                "supporting_count": active_review_queue_count,
                "blocker": "",
            },
            {
                "gate_component": "governance_gates",
                "component_state": "closed",
                "supporting_count": closed_gate_count,
                "blocker": "execution_authority_gate_and_live_like_opening_gate_still_closed",
            },
            {
                "gate_component": "serving_live_like",
                "component_state": "materialized_but_blocked",
                "supporting_count": materialized_but_blocked_count,
                "blocker": "live_like_views_materialized_but_governance_and_execution_gates_remain_closed",
            },
            {
                "gate_component": "replay_binding",
                "component_state": "blocked",
                "supporting_count": 1 if replay_execution_backlog else 0,
                "blocker": "execution_binding_backlog_present",
            },
            {
                "gate_component": "local_ingest_floor",
                "component_state": "active_local_only",
                "supporting_count": active_local_ingest_count,
                "blocker": "network_sources_are_policy_bound_but_not_runtime_activated",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "active_local_ingest_count": active_local_ingest_count,
            "policy_bound_adapter_count": policy_bound_adapter_count,
            "active_review_queue_count": active_review_queue_count,
            "closed_gate_count": closed_gate_count,
            "materialized_live_like_view_count": materialized_but_blocked_count,
            "replay_execution_backlog_present": replay_execution_backlog,
            "live_like_ready_now": False,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_live_like_gate_refined_but_not_satisfied",
        }
        interpretation = [
            "The source-side blocker is now more precise: network fetch is policy-bound, but still awaits selective activation.",
            "Live-like remains blocked for governance and replay reasons even after source-side ambiguity is reduced.",
        ]
        return V134MEAShareLiveLikeGateRefinementAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MEAShareLiveLikeGateRefinementAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MEAShareLiveLikeGateRefinementAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134me_a_share_live_like_gate_refinement_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
