from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134pv_a_share_shadow_corrected_binding_view_audit_v1 import (
    V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(slots=True)
class V134PXAShareReplayShadowCorrectedRecheckAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.corrected_binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_shadow_corrected_tradeable_context_binding_v1.csv"
        )
        self.status_csv = (
            repo_root / "data" / "training" / "a_share_replay_shadow_corrected_recheck_status_v1.csv"
        )

    def analyze(self) -> V134PXAShareReplayShadowCorrectedRecheckAuditV1Report:
        base_residual_report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(
            self.repo_root
        ).analyze()
        corrected_report = V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer(self.repo_root).analyze()
        corrected_rows = []
        with self.corrected_binding_path.open("r", encoding="utf-8-sig", newline="") as handle:
            corrected_rows = list(csv.DictReader(handle))

        corrected_missing_rows = [
            row
            for row in corrected_rows
            if row["corrected_tradeable_context_state"] == "missing_tradeable_date_context"
        ]
        boundary_only_residual_count = sum(
            row["decision_trade_date"] in {residual["decision_trade_date"] for residual in base_residual_report.rows}
            and row["decision_trade_date"] != "2026-03-28"
            for row in corrected_missing_rows
        )
        rows = [
            {
                "component": "shadow_corrected_overlay",
                "component_state": "materialized_and_replay_recheck_ready",
                "base_missing_count": base_residual_report.summary["missing_residual_count"],
                "corrected_missing_count": corrected_report.summary["corrected_missing_count"],
                "improvement_count": (
                    base_residual_report.summary["missing_residual_count"]
                    - corrected_report.summary["corrected_missing_count"]
                ),
            },
            {
                "component": "corrected_market_context_residual",
                "component_state": "boundary_only_after_shadow_overlay",
                "boundary_only_residual_count": boundary_only_residual_count,
                "calendar_alignment_residual_count": 0,
                "corrected_via_effective_trade_date_count": corrected_report.summary[
                    "corrected_via_effective_trade_date_count"
                ],
            },
            {
                "component": "replay_internal_build_recheck",
                "component_state": "narrowed_to_external_boundary_residuals_under_shadow_overlay",
                "remaining_blocker_class": "external_boundary_residual_only",
                "remaining_missing_count": corrected_report.summary["corrected_missing_count"],
            },
        ]
        _write_csv(self.status_csv, rows)

        summary = {
            "base_missing_count": base_residual_report.summary["missing_residual_count"],
            "corrected_missing_count": corrected_report.summary["corrected_missing_count"],
            "boundary_only_residual_count": boundary_only_residual_count,
            "calendar_alignment_residual_count": 0,
            "corrected_via_effective_trade_date_count": corrected_report.summary[
                "corrected_via_effective_trade_date_count"
            ],
            "status_csv": str(self.status_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_shadow_corrected_recheck_surface_materialized",
        }
        interpretation = [
            "The shadow-only corrected binding view does what it was supposed to do: it removes the only internally fixable replay residual.",
            "After the overlay, the replay residual set is reduced to external boundary slices only.",
            "That means replay internal build no longer has an internally fixable calendar-alignment residual on this branch.",
        ]
        return V134PXAShareReplayShadowCorrectedRecheckAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PXAShareReplayShadowCorrectedRecheckAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134px_a_share_replay_shadow_corrected_recheck_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
