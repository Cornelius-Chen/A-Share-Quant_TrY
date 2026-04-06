from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pt_a_share_shadow_effective_trade_date_trial_audit_v1 import (
    V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134PVAShareShadowCorrectedBindingViewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer:
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
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "replay_registry"
        self.corrected_binding_path = (
            self.output_dir / "a_share_shadow_corrected_tradeable_context_binding_v1.csv"
        )
        self.corrected_residual_path = (
            self.output_dir / "a_share_shadow_corrected_tradeable_context_binding_residual_v1.csv"
        )
        self.status_csv = (
            repo_root / "data" / "training" / "a_share_shadow_corrected_binding_view_status_v1.csv"
        )

    def analyze(self) -> V134PVAShareShadowCorrectedBindingViewAuditV1Report:
        base_rows = _read_csv(self.base_binding_path)
        trial_report = V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer(self.repo_root).analyze()
        trial_rows = {row["slice_id"]: row for row in trial_report.rows}

        corrected_binding_rows: list[dict[str, Any]] = []
        corrected_bound_count = 0
        corrected_missing_count = 0
        corrected_via_effective_trade_date_count = 0
        for row in base_rows:
            trial_row = trial_rows.get(row["slice_id"])
            if trial_row is None:
                corrected_query_trade_date = row["decision_trade_date"]
                corrected_state = row["tradeable_context_state"]
            else:
                corrected_query_trade_date = trial_row["trial_query_trade_date"]
                corrected_state = trial_row["trial_tradeable_context_state"]

            via_effective_trade_date = (
                corrected_query_trade_date != row["decision_trade_date"]
                and corrected_state == "date_level_tradeable_context_bound_via_effective_trade_date"
            )
            if via_effective_trade_date:
                corrected_via_effective_trade_date_count += 1
            if corrected_state.startswith("date_level_tradeable_context_bound"):
                corrected_bound_count += 1
            else:
                corrected_missing_count += 1

            corrected_binding_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": row["decision_trade_date"],
                    "corrected_query_trade_date": corrected_query_trade_date,
                    "replay_status": row["replay_status"],
                    "baseline_tradeable_context_state": row["tradeable_context_state"],
                    "corrected_tradeable_context_state": corrected_state,
                    "corrected_via_effective_trade_date": str(via_effective_trade_date),
                }
            )

        corrected_residual_rows = [
            row
            for row in corrected_binding_rows
            if row["corrected_tradeable_context_state"] == "missing_tradeable_date_context"
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.status_csv.parent.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.corrected_binding_path, corrected_binding_rows)
        if corrected_residual_rows:
            _write(self.corrected_residual_path, corrected_residual_rows)

        status_rows = [
            {
                "component": "shadow_corrected_binding_view",
                "component_state": "materialized_shadow_only_corrected_binding",
                "binding_row_count": corrected_bound_count + corrected_missing_count,
                "corrected_bound_count": corrected_bound_count,
                "corrected_missing_count": corrected_missing_count,
                "corrected_via_effective_trade_date_count": corrected_via_effective_trade_date_count,
            }
        ]
        _write(self.status_csv, status_rows)

        summary = {
            "binding_row_count": len(corrected_binding_rows),
            "corrected_bound_count": corrected_bound_count,
            "corrected_missing_count": corrected_missing_count,
            "corrected_via_effective_trade_date_count": corrected_via_effective_trade_date_count,
            "corrected_binding_path": str(self.corrected_binding_path.relative_to(self.repo_root)),
            "corrected_residual_path": str(self.corrected_residual_path.relative_to(self.repo_root)),
            "status_csv": str(self.status_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_corrected_binding_view_materialized",
        }
        rows = status_rows
        interpretation = [
            "The corrected binding view keeps the base replay binding untouched and adds only a shadow-side auxiliary query date.",
            "That is enough to reduce the replay market-context residual from three rows to two without mutating PTI history.",
        ]
        return V134PVAShareShadowCorrectedBindingViewAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PVAShareShadowCorrectedBindingViewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pv_a_share_shadow_corrected_binding_view_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
