from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)


@dataclass(slots=True)
class V112ASCPOBoundedImplementationBackfillReport:
    summary: dict[str, Any]
    patch_application_rows: list[dict[str, Any]]
    coverage_rows: list[dict[str, Any]]
    sample_rows_preview: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "patch_application_rows": self.patch_application_rows,
            "coverage_rows": self.coverage_rows,
            "sample_rows_preview": self.sample_rows_preview,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ASCPOBoundedImplementationBackfillAnalyzer:
    ROLE_WEIGHTS = {
        "core_anchor": 1.00,
        "core_beta": 1.00,
        "core_platform_confirmation": 1.00,
        "adjacent_bridge": 0.75,
        "adjacent_high_beta_extension": 0.75,
        "branch_extension": 0.50,
        "late_extension": 0.50,
        "spillover_candidate": 0.25,
        "weak_memory": 0.25,
        "pending_ambiguous": 0.25,
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        patch_spec_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112ASCPOBoundedImplementationBackfillReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112as_now")):
            raise ValueError("V1.12AS must be open before bounded implementation backfill runs.")

        patch_spec_summary = dict(patch_spec_payload.get("summary", {}))
        if int(patch_spec_summary.get("total_patch_rule_count", 0)) != 6:
            raise ValueError("V1.12AS expects the frozen 6-rule patch spec from V1.12AR.")

        truth_rows = [
            row
            for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))
            if bool(row.get("include_in_truth_candidate_rows"))
        ]
        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        ao_analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = ao_analyzer._build_samples(  # noqa: SLF001
            truth_rows=truth_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: (item.trade_date, item.symbol))
        if not samples:
            raise ValueError("V1.12AS requires sample rows to backfill implementation fields.")

        truth_index = {str(row.get("symbol")): row for row in truth_rows}
        frame = pd.DataFrame(
            {
                "trade_date": [sample.trade_date for sample in samples],
                "symbol": [sample.symbol for sample in samples],
                "stage_family": [sample.stage_family for sample in samples],
                "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
                "ret_5": [sample.feature_values["ret_5"] for sample in samples],
                "ret_20": [sample.feature_values["ret_20"] for sample in samples],
                "price_vs_ma20": [sample.feature_values["price_vs_ma20"] for sample in samples],
                "volume_ratio_5_20": [sample.feature_values["volume_ratio_5_20"] for sample in samples],
                "cohort_layer": [str(truth_index[sample.symbol]["cohort_layer"]) for sample in samples],
            }
        )
        frame["weight"] = frame["cohort_layer"].map(self.ROLE_WEIGHTS).astype(float)
        frame["positive_participation"] = (
            (frame["ret_5"] > 0).astype(float) + (frame["price_vs_ma20"] > 0).astype(float)
        ) / 2.0

        board_daily = (
            frame.groupby("trade_date", as_index=False)
            .apply(self._board_daily_row)
            .reset_index(drop=True)
            .sort_values("trade_date")
            .reset_index(drop=True)
        )
        board_daily["turnover_percentile_20"] = self._trailing_percentile(board_daily["board_proxy"])
        board_daily["turnover_pressure_state"] = board_daily["turnover_percentile_20"].map(
            self._turnover_state
        )

        frame = frame.merge(board_daily, on="trade_date", how="left")
        frame["vendor_source_class"] = "bounded_cohort_reconstructed_proxy"
        frame["fallback_reason"] = "none_primary_proxy"
        frame["disclosed_vs_inferred_flag"] = frame["stage_family"].map(self._calendar_disclosure_mode)
        frame["window_uncertainty_state"] = frame["stage_family"].map(self._calendar_uncertainty_state)
        frame["confidence_tier"] = frame["stage_family"].map(self._calendar_confidence_tier)
        frame["prior_anchor_reference"] = frame["stage_family"].map(self._calendar_anchor_reference)
        frame["rollforward_reason"] = frame["stage_family"].map(self._calendar_rollforward_reason)

        patch_application_rows = [
            {
                "rule_name": "board_vendor_selection_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every current truth-row sample now records vendor_source_class and fallback_reason.",
            },
            {
                "rule_name": "breadth_formula_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every sample now attaches weighted cohort breadth from same-day observable truth-row participation.",
            },
            {
                "rule_name": "turnover_normalization_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every sample now attaches trailing turnover percentile and mapped pressure state.",
            },
            {
                "rule_name": "expected_window_fill_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every sample now records disclosed-vs-inferred posture and window uncertainty state.",
            },
            {
                "rule_name": "confidence_tier_mapping_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every sample now records a bounded confidence tier.",
            },
            {
                "rule_name": "calendar_rollforward_rule",
                "applied": True,
                "coverage_ratio": 1.0,
                "reading": "Every sample now records prior-anchor reference and rollforward reason.",
            },
        ]

        coverage_rows = [
            {
                "coverage_name": "board_backfill_sample_coverage",
                "coverage_ratio": 1.0,
                "covered_sample_count": int(len(frame)),
                "reading": "Board implementation columns are fully backfilled on current truth rows.",
            },
            {
                "coverage_name": "calendar_backfill_sample_coverage",
                "coverage_ratio": 1.0,
                "covered_sample_count": int(len(frame)),
                "reading": "Calendar implementation columns are fully attached as bounded point-in-time posture fields.",
            },
            {
                "coverage_name": "unique_trade_dates_with_board_proxy",
                "coverage_ratio": 1.0,
                "covered_sample_count": int(frame["trade_date"].nunique()),
                "reading": "A bounded board proxy now exists on every observed truth-row trade date.",
            },
        ]

        preview_columns = [
            "trade_date",
            "symbol",
            "stage_family",
            "vendor_source_class",
            "weighted_breadth_ratio",
            "turnover_pressure_state",
            "disclosed_vs_inferred_flag",
            "window_uncertainty_state",
            "confidence_tier",
            "rollforward_reason",
        ]
        sample_rows_preview = (
            frame.loc[:, preview_columns].head(14).to_dict(orient="records")
        )

        summary = {
            "acceptance_posture": "freeze_v112as_cpo_bounded_implementation_backfill_v1",
            "truth_candidate_row_count": len(truth_rows),
            "sample_count": int(len(frame)),
            "unique_trade_date_count": int(frame["trade_date"].nunique()),
            "patch_rule_count_applied": 6,
            "board_backfill_coverage_ratio": 1.0,
            "calendar_backfill_coverage_ratio": 1.0,
            "next_lawful_move": "rerun_current_truth_rows_with_patched_board_and_calendar_features_before_any_row_geometry_widen",
            "allow_row_geometry_widen_now": False,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12AS applies the frozen implementation rules on the current truth rows without widening geometry.",
            "This does not yet open row-geometry widen; it only removes the excuse that board/calendar rules remain undefined.",
            "The next lawful move is a post-patch rerun on the current truth rows before deciding whether widen is warranted.",
        ]
        return V112ASCPOBoundedImplementationBackfillReport(
            summary=summary,
            patch_application_rows=patch_application_rows,
            coverage_rows=coverage_rows,
            sample_rows_preview=sample_rows_preview,
            interpretation=interpretation,
        )

    def _board_daily_row(self, group: pd.DataFrame) -> pd.Series:
        weight_sum = float(group["weight"].sum())
        weighted_breadth_ratio = (
            float((group["weight"] * group["positive_participation"]).sum()) / weight_sum if weight_sum else 0.0
        )
        board_proxy = (
            float((group["weight"] * (group["volume_ratio_5_20"] + group["positive_participation"])).sum()) / weight_sum
            if weight_sum
            else 0.0
        )
        return pd.Series(
            {
                "weighted_breadth_ratio": round(weighted_breadth_ratio, 6),
                "board_proxy": round(board_proxy, 6),
            }
        )

    def _trailing_percentile(self, series: pd.Series) -> pd.Series:
        values = series.astype(float).tolist()
        out: list[float] = []
        for idx, value in enumerate(values):
            start = max(0, idx - 19)
            window = values[start : idx + 1]
            rank = sum(1 for item in window if item <= value)
            out.append(rank / len(window))
        return pd.Series(out, index=series.index)

    def _turnover_state(self, percentile: float) -> str:
        if percentile < 0.25:
            return "calm"
        if percentile < 0.60:
            return "normal"
        if percentile < 0.85:
            return "elevated"
        return "exhausted"

    def _calendar_disclosure_mode(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "inferred_cadence_window",
            "ignition": "near_disclosed_window",
            "main_markup": "near_disclosed_window",
            "diffusion": "followthrough_window",
            "laggard_catchup": "expired_anchor_window",
            "divergence_and_decay": "archived_anchor_window",
        }[stage_family]

    def _calendar_uncertainty_state(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "high",
            "ignition": "medium",
            "main_markup": "medium",
            "diffusion": "medium",
            "laggard_catchup": "low",
            "divergence_and_decay": "low",
        }[stage_family]

    def _calendar_confidence_tier(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "tier3",
            "ignition": "tier2",
            "main_markup": "tier2",
            "diffusion": "tier3",
            "laggard_catchup": "tier4",
            "divergence_and_decay": "tier4",
        }[stage_family]

    def _calendar_anchor_reference(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "prior_cycle_cadence_reference",
            "ignition": "current_cycle_anchor_active",
            "main_markup": "current_cycle_anchor_active",
            "diffusion": "current_cycle_followthrough",
            "laggard_catchup": "expired_cycle_anchor",
            "divergence_and_decay": "expired_cycle_anchor",
        }[stage_family]

    def _calendar_rollforward_reason(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "carry_prior_cadence_placeholder",
            "ignition": "active_anchor_no_rollforward",
            "main_markup": "active_anchor_no_rollforward",
            "diffusion": "followthrough_hold",
            "laggard_catchup": "archive_without_new_cycle",
            "divergence_and_decay": "archive_without_new_cycle",
        }[stage_family]


def write_v112as_cpo_bounded_implementation_backfill_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ASCPOBoundedImplementationBackfillReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
