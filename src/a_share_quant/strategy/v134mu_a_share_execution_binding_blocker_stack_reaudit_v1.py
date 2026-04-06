from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)
from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134MUAShareExecutionBindingBlockerStackReauditV1Report:
    summary: dict[str, Any]
    blocker_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "blocker_rows": self.blocker_rows,
            "interpretation": self.interpretation,
        }


class V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.gate_path = (
            repo_root / "data" / "reference" / "info_center" / "governance_registry" / "a_share_promotion_gate_registry_v1.csv"
        )
        self.live_like_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_live_like_view_materialization_registry_v1.csv"
        )
        self.tradeable_gap_path = (
            repo_root / "data" / "training" / "a_share_replay_market_coverage_gap_status_v1.csv"
        )
        self.cost_model_path = (
            repo_root / "data" / "training" / "a_share_replay_cost_model_foundation_status_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_execution_binding_blocker_stack_reaudit_v1.csv"
        )

    def analyze(self) -> V134MUAShareExecutionBindingBlockerStackReauditV1Report:
        gate_rows = _read_csv(self.gate_path)
        live_like_rows = _read_csv(self.live_like_path)
        tradeable_gap_rows = _read_csv(self.tradeable_gap_path)
        cost_model_rows = _read_csv(self.cost_model_path)
        residual_report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()
        corrected_recheck_report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()
        source_precondition_report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(
            self.repo_root
        ).analyze()

        execution_journal_stub_count = 0
        for row in cost_model_rows:
            if row["component"] == "shadow_execution_journal":
                execution_journal_stub_count = int(row["coverage_note"].split("=")[1].strip())
                break
        daily_gap_count = sum(row["daily_present"] != "True" for row in tradeable_gap_rows)

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
                "blocker_id": "source_promotion_preconditions_unsatisfied",
                "blocker_layer": "source_activation",
                "blocker_state": "active",
                "blocking_reason": (
                    f"unsatisfied_precondition_count = {source_precondition_report.summary['unsatisfied_count']}"
                ),
            },
            {
                "blocker_id": "replay_execution_journal_stub_only",
                "blocker_layer": "replay",
                "blocker_state": "active",
                "blocking_reason": f"execution_journal_stub_count = {execution_journal_stub_count}",
            },
            {
                "blocker_id": "replay_market_context_boundary_residuals",
                "blocker_layer": "replay",
                "blocker_state": "active",
                "blocking_reason": (
                    f"base_missing_count = {corrected_recheck_report.summary['base_missing_count']}; "
                    f"corrected_missing_count = {corrected_recheck_report.summary['corrected_missing_count']}; "
                    f"boundary_only_residual_count = {corrected_recheck_report.summary['boundary_only_residual_count']}"
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
            "source_blocker_count": sum(row["blocker_layer"] == "source_activation" for row in blocker_rows),
            "replay_blocker_count": sum(row["blocker_layer"] == "replay" for row in blocker_rows),
            "serving_blocker_count": sum(row["blocker_layer"] == "serving" for row in blocker_rows),
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_execution_binding_blocker_stack_reaudited_and_refined",
        }
        interpretation = [
            "Execution binding blockers are now re-audited against the latest source-side and replay-side registries.",
            "The replay blocker is no longer a generic cost-model phrase; it is split into execution-journal stub and two remaining external boundary residuals after the shadow-only corrected recheck.",
            "On the source side, manual batch-one approval is now complete, so only the remaining promotion precondition blocker stays active.",
        ]
        return V134MUAShareExecutionBindingBlockerStackReauditV1Report(
            summary=summary, blocker_rows=blocker_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MUAShareExecutionBindingBlockerStackReauditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mu_a_share_execution_binding_blocker_stack_reaudit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
