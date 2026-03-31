from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CKNeutralResidualFamilyReviewReport:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "residual_rows": self.residual_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CKNeutralResidualFamilyReviewAnalyzer:
    def analyze(
        self,
        *,
        cj_payload: dict[str, Any],
    ) -> V112CKNeutralResidualFamilyReviewReport:
        summary = dict(cj_payload.get("summary", {}))
        packaging_rows = list(cj_payload.get("packaging_window_rows", []))
        residual_trade_rows = list(cj_payload.get("residual_trade_rows", []))

        family_rows: list[dict[str, Any]] = []
        residual_rows: list[dict[str, Any]] = []

        missed_packaging = [row for row in packaging_rows if str(row.get("residual_reading")) == "missed_packaging_eligibility_window"]
        if missed_packaging:
            family_rows.append(
                {
                    "residual_family": "packaging_eligibility_miss_while_cash",
                    "family_type": "missed_opportunity",
                    "row_count": len(missed_packaging),
                    "recommended_probe": "do_not_change_packaging_template; inspect neutral cash discipline around packaging eligibility windows",
                }
            )
            residual_rows.extend(
                {
                    "residual_family": "packaging_eligibility_miss_while_cash",
                    "trade_date": str(row.get("trade_date")),
                    "symbol": str(row.get("symbol")),
                    "reading": str(row.get("residual_reading")),
                }
                for row in missed_packaging
            )

        core_leader_overstay = [
            row
            for row in residual_trade_rows
            if str(row.get("symbol")) == "300308" and float(row.get("realized_forward_return_20d", 0.0)) < 0.0
        ]
        if core_leader_overstay:
            family_rows.append(
                {
                    "residual_family": "core_module_leader_mature_markup_overstay",
                    "family_type": "drawdown_failure",
                    "row_count": len(core_leader_overstay),
                    "recommended_probe": "open holding-veto or maturity-overstay probe on core leader windows",
                }
            )
            residual_rows.extend(
                {
                    "residual_family": "core_module_leader_mature_markup_overstay",
                    "entry_date": str(row.get("entry_date")),
                    "symbol": str(row.get("symbol")),
                    "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                    "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                }
                for row in core_leader_overstay
            )

        high_beta_drawdown = [
            row
            for row in residual_trade_rows
            if str(row.get("symbol")) == "300502" and float(row.get("path_max_drawdown", 0.0)) <= -0.15
        ]
        if high_beta_drawdown:
            family_rows.append(
                {
                    "residual_family": "high_beta_core_module_expression_risk",
                    "family_type": "drawdown_tolerance_failure",
                    "row_count": len(high_beta_drawdown),
                    "recommended_probe": "inspect whether de-risk sizing or half-life control is needed on high-beta core windows",
                }
            )
            residual_rows.extend(
                {
                    "residual_family": "high_beta_core_module_expression_risk",
                    "entry_date": str(row.get("entry_date")),
                    "symbol": str(row.get("symbol")),
                    "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                    "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                }
                for row in high_beta_drawdown
            )

        summary_out = {
            "acceptance_posture": "freeze_v112ck_neutral_residual_family_review_v1",
            "baseline_total_return": summary.get("baseline_total_return"),
            "baseline_max_drawdown": summary.get("baseline_max_drawdown"),
            "packaging_injection_immediate_gain": False,
            "residual_family_count": len(family_rows),
            "dominant_residual_family": family_rows[0]["residual_family"] if family_rows else "none",
            "recommended_next_posture": "keep_packaging_frozen_and_open_ex_packaging_residual_probe_on_core_leader_or_high_beta_core_windows",
        }
        interpretation = [
            "V1.12CK converts the constrained replay result into explicit residual families so the project does not confuse packaging template success with full neutral-path resolution.",
            "After packaging is frozen, the remaining issues are dominated by non-packaging residuals and by missed packaging eligibility windows rather than by packaging veto design itself.",
        ]
        return V112CKNeutralResidualFamilyReviewReport(
            summary=summary_out,
            family_rows=family_rows,
            residual_rows=residual_rows,
            interpretation=interpretation,
        )


def write_v112ck_neutral_residual_family_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CKNeutralResidualFamilyReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
