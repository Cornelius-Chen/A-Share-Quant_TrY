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
class MaterializedAShareReplayTradeableContextBindingV1:
    summary: dict[str, Any]
    binding_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareReplayTradeableContextBindingV1:
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
            / "a_share_limit_halt_semantic_surface_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "replay_registry"
        self.binding_path = self.output_dir / "a_share_replay_tradeable_context_binding_v1.csv"
        self.residual_path = self.output_dir / "a_share_replay_tradeable_context_binding_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_replay_tradeable_context_binding_manifest_v1.json"

    def materialize(self) -> MaterializedAShareReplayTradeableContextBindingV1:
        shadow_rows = _read_csv(self.shadow_surface_path)
        limit_rows = _read_csv(self.limit_halt_path)
        by_date: dict[str, list[dict[str, str]]] = {}
        for row in limit_rows:
            raw_trade_date = row["trade_date"]
            normalized_trade_date = (
                f"{raw_trade_date[:4]}-{raw_trade_date[4:6]}-{raw_trade_date[6:]}"
                if len(raw_trade_date) == 8 and raw_trade_date.isdigit()
                else raw_trade_date
            )
            by_date.setdefault(normalized_trade_date, []).append(row)

        binding_rows: list[dict[str, Any]] = []
        date_level_bound_count = 0
        missing_date_context_count = 0
        for row in shadow_rows:
            trade_date = row["decision_trade_date"]
            date_rows = by_date.get(trade_date, [])
            if date_rows:
                date_level_bound_count += 1
                context_state = "date_level_tradeable_context_bound"
                limit_hit_symbol_count = sum(
                    r["limit_up_hit"] == "True" or r["limit_down_hit"] == "True" for r in date_rows
                )
                suspend_symbol_count = sum(r["halt_or_suspend_flag"] == "True" for r in date_rows)
            else:
                missing_date_context_count += 1
                context_state = "missing_tradeable_date_context"
                limit_hit_symbol_count = 0
                suspend_symbol_count = 0
            binding_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": trade_date,
                    "replay_status": row["replay_status"],
                    "tradeable_context_state": context_state,
                    "limit_hit_symbol_count": limit_hit_symbol_count,
                    "suspend_symbol_count": suspend_symbol_count,
                }
            )

        residual_rows = [
            {
                "residual_class": "symbol_level_binding_missing",
                "residual_reason": "tradeable context is only date-level and not yet symbol-bound to replay decisions",
            },
            {
                "residual_class": "missing_tradeable_dates_remain",
                "residual_reason": "some shadow slices still have no date-level tradeable context coverage",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.binding_path, binding_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "binding_row_count": len(binding_rows),
            "date_level_bound_count": date_level_bound_count,
            "missing_date_context_count": missing_date_context_count,
            "binding_path": str(self.binding_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareReplayTradeableContextBindingV1(
            summary=summary, binding_rows=binding_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareReplayTradeableContextBindingV1(repo_root).materialize()
    print(result.summary["binding_path"])


if __name__ == "__main__":
    main()
