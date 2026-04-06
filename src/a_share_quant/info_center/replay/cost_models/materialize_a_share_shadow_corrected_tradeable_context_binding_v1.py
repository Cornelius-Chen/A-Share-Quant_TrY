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
class MaterializedAShareShadowCorrectedTradeableContextBindingV1:
    summary: dict[str, Any]
    binding_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareShadowCorrectedTradeableContextBindingV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_replay_tradeable_context_binding_v1.csv"
        )
        self.trial_status_path = (
            repo_root / "data" / "training" / "a_share_shadow_effective_trade_date_trial_status_v1.csv"
        )
        self.output_dir = repo_root / "data" / "derived" / "info_center" / "replay" / "shadow"
        self.binding_path = self.output_dir / "a_share_shadow_corrected_tradeable_context_binding_v1.csv"
        self.residual_path = self.output_dir / "a_share_shadow_corrected_tradeable_context_binding_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_shadow_corrected_tradeable_context_binding_manifest_v1.json"

    def materialize(self) -> MaterializedAShareShadowCorrectedTradeableContextBindingV1:
        base_rows = _read_csv(self.base_binding_path)
        trial_rows = _read_csv(self.trial_status_path)
        trial_by_slice = {row["slice_id"]: row for row in trial_rows}

        corrected_rows: list[dict[str, Any]] = []
        corrected_bound_count = 0
        corrected_missing_count = 0
        corrected_via_effective_trade_date_count = 0
        for row in base_rows:
            trial_row = trial_by_slice.get(row["slice_id"])
            corrected_state = row["tradeable_context_state"]
            effective_trade_date = row["decision_trade_date"]
            if trial_row:
                effective_trade_date = trial_row["trial_query_trade_date"]
                corrected_state = trial_row["trial_tradeable_context_state"]
                if corrected_state == "date_level_tradeable_context_bound_via_effective_trade_date":
                    corrected_via_effective_trade_date_count += 1

            if corrected_state.startswith("date_level_tradeable_context_bound"):
                corrected_bound_count += 1
            else:
                corrected_missing_count += 1

            corrected_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": row["decision_trade_date"],
                    "effective_trade_date": effective_trade_date,
                    "baseline_tradeable_context_state": row["tradeable_context_state"],
                    "corrected_tradeable_context_state": corrected_state,
                }
            )

        residual_rows = [
            row for row in corrected_rows if row["corrected_tradeable_context_state"] == "missing_tradeable_date_context"
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.binding_path, corrected_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "binding_row_count": len(corrected_rows),
            "corrected_bound_count": corrected_bound_count,
            "corrected_missing_count": corrected_missing_count,
            "corrected_via_effective_trade_date_count": corrected_via_effective_trade_date_count,
            "binding_path": str(self.binding_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareShadowCorrectedTradeableContextBindingV1(
            summary=summary,
            binding_rows=corrected_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareShadowCorrectedTradeableContextBindingV1(repo_root).materialize()
    print(result.summary["binding_path"])


if __name__ == "__main__":
    main()
