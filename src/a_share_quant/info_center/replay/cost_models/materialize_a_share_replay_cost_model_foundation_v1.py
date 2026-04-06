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
class MaterializedAShareReplayCostModelFoundationV1:
    summary: dict[str, Any]
    cost_model_rows: list[dict[str, Any]]
    execution_journal_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareReplayCostModelFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.shadow_surface_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.limit_halt_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_surface_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "replay_registry"
        self.cost_model_path = self.output_dir / "a_share_replay_cost_model_registry_v1.csv"
        self.execution_journal_path = self.output_dir / "a_share_shadow_execution_journal_stub_v1.csv"
        self.residual_path = self.output_dir / "a_share_replay_cost_model_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_replay_cost_model_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareReplayCostModelFoundationV1:
        shadow_rows = _read_csv(self.shadow_surface_path)
        limit_rows = _read_csv(self.limit_halt_path)
        halt_or_suspend_count = sum(row["halt_or_suspend_flag"] == "True" for row in limit_rows)
        limit_hit_count = sum(
            row["limit_up_hit"] == "True" or row["limit_down_hit"] == "True" for row in limit_rows
        )

        cost_model_rows = [
            {
                "cost_model_id": "shadow_basic_equity_cost_v1",
                "cost_scope": "baseline_non_limit_non_suspend",
                "model_state": "foundation_stub",
                "slippage_bps": "5",
                "fee_bps": "3",
            },
            {
                "cost_model_id": "shadow_limit_guarded_cost_v1",
                "cost_scope": "limit_hit_or_near_limit",
                "model_state": "foundation_stub",
                "slippage_bps": "25",
                "fee_bps": "3",
            },
            {
                "cost_model_id": "shadow_suspend_blocked_cost_v1",
                "cost_scope": "halt_or_suspend",
                "model_state": "foundation_block_rule",
                "slippage_bps": "NA",
                "fee_bps": "NA",
            },
        ]

        execution_journal_rows = [
            {
                "slice_id": row["slice_id"],
                "decision_trade_date": row["decision_trade_date"],
                "replay_status": row["replay_status"],
                "execution_journal_state": "stub_unbound",
            }
            for row in shadow_rows
        ]

        residual_rows = [
            {
                "residual_class": "symbol_tradeable_state_not_bound",
                "residual_reason": "cost models exist but are not yet symbol-bound at replay decision time",
            },
            {
                "residual_class": "execution_journal_not_lawful",
                "residual_reason": "shadow execution journal remains a stub and does not authorize real execution linkage",
            },
            {
                "residual_class": "market_context_alignment_pending",
                "residual_reason": "shadow slices still include missing-market-context cases and cannot all consume a unified cost model",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.cost_model_path, cost_model_rows)
        _write(self.execution_journal_path, execution_journal_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "cost_model_count": len(cost_model_rows),
            "execution_journal_stub_count": len(execution_journal_rows),
            "limit_hit_count": limit_hit_count,
            "halt_or_suspend_count": halt_or_suspend_count,
            "cost_model_path": str(self.cost_model_path.relative_to(self.repo_root)),
            "execution_journal_path": str(self.execution_journal_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareReplayCostModelFoundationV1(
            summary=summary,
            cost_model_rows=cost_model_rows,
            execution_journal_rows=execution_journal_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareReplayCostModelFoundationV1(repo_root).materialize()
    print(result.summary["cost_model_path"])


if __name__ == "__main__":
    main()
