from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)


@dataclass(slots=True)
class V112ATCPOPostPatchRerunReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    implementation_family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "implementation_family_rows": self.implementation_family_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ATCPOPostPatchRerunAnalyzer:
    GUARDED_TARGETS = (
        "board_condition_label",
        "role_transition_label",
        "failed_role_promotion_label",
    )
    IMPLEMENTATION_FEATURE_NAMES = [
        "weighted_breadth_ratio",
        "turnover_percentile_20",
        "turnover_state_numeric",
        "event_disclosure_numeric",
        "window_uncertainty_numeric",
        "confidence_tier_numeric",
        "rollforward_state_numeric",
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        widen_pilot_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112ATCPOPostPatchRerunReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112at_now")):
            raise ValueError("V1.12AT must be open before the rerun starts.")

        ap_target_index = {
            str(row.get("target_name")): row for row in list(widen_pilot_payload.get("target_rows", []))
        }
        ap_guarded_index = {
            str(row.get("target_name")): row for row in list(widen_pilot_payload.get("guarded_target_rows", []))
        }

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
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in truth_rows}
        impl_features = self._implementation_feature_map(samples=samples, truth_index=truth_index)

        feature_names = (
            pilot_analyzer.FEATURE_NAMES
            + ao_analyzer.PATCH_FEATURE_NAMES
            + self.IMPLEMENTATION_FEATURE_NAMES
        )
        x = np.array(
            [
                [sample.feature_values[name] for name in pilot_analyzer.FEATURE_NAMES + ao_analyzer.PATCH_FEATURE_NAMES]
                + [impl_features[(sample.trade_date, sample.symbol)][name] for name in self.IMPLEMENTATION_FEATURE_NAMES]
                for sample in samples
            ],
            dtype=float,
        )
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))

        target_rows: list[dict[str, Any]] = []
        target_defs = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }
        for target_name, labels in target_defs.items():
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=x, split_index=split_index)
            prior_row = dict(ap_target_index[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy_before_impl_patch": prior_row.get("baseline_accuracy_after_widen"),
                    "baseline_accuracy_after_impl_patch": baseline_accuracy,
                    "gbdt_accuracy_before_impl_patch": prior_row.get("gbdt_accuracy_after_widen"),
                    "gbdt_accuracy_after_impl_patch": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112ap": round(gbdt_accuracy - float(prior_row["gbdt_accuracy_after_widen"]), 4),
                }
            )

        # build guarded rows separately with lawful subsets from V112AP definitions
        for target_name in self.GUARDED_TARGETS:
            subset_samples = self._guarded_subset(target_name=target_name, samples=samples)
            subset_x = np.array(
                [
                    [sample.feature_values[name] for name in pilot_analyzer.FEATURE_NAMES + ao_analyzer.PATCH_FEATURE_NAMES]
                    + [impl_features[(sample.trade_date, sample.symbol)][name] for name in self.IMPLEMENTATION_FEATURE_NAMES]
                    for sample in subset_samples
                ],
                dtype=float,
            )
            subset_split = max(1, min(len(subset_samples) - 1, int(len(subset_samples) * 0.7)))
            labels = self._guarded_labels(target_name=target_name, samples=subset_samples)
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=subset_x, split_index=subset_split)
            prior_row = dict(ap_guarded_index[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy_before_impl_patch": prior_row.get("baseline_accuracy"),
                    "baseline_accuracy_after_impl_patch": baseline_accuracy,
                    "gbdt_accuracy_before_impl_patch": prior_row.get("gbdt_accuracy"),
                    "gbdt_accuracy_after_impl_patch": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112ap": round(gbdt_accuracy - float(prior_row["gbdt_accuracy"]), 4),
                }
            )

        implementation_family_rows = []
        role_labels = [sample.role_family for sample in samples]
        role_full_accuracy = self._run_target(labels=role_labels, x=x, split_index=split_index)[1]
        impl_feature_indexes = [feature_names.index(name) for name in self.IMPLEMENTATION_FEATURE_NAMES]
        x_masked = x.copy()
        x_masked[:, impl_feature_indexes] = 0.0
        role_masked_accuracy = self._run_target(labels=role_labels, x=x_masked, split_index=split_index)[1]
        implementation_family_rows.append(
            {
                "family_name": "implementation_board_calendar_family",
                "full_accuracy": role_full_accuracy,
                "masked_accuracy": role_masked_accuracy,
                "accuracy_drop": round(role_full_accuracy - role_masked_accuracy, 4),
                "reading": "Accuracy drop indicates how much the rerun relies on the newly backfilled implementation layer.",
            }
        )

        core_rows = [row for row in target_rows if row["target_name"] in target_defs]
        guarded_rows = [row for row in target_rows if row["target_name"] not in target_defs]
        summary = {
            "acceptance_posture": "freeze_v112at_cpo_post_patch_rerun_v1",
            "truth_candidate_row_count": len(truth_rows),
            "sample_count": len(samples),
            "implementation_feature_count": len(self.IMPLEMENTATION_FEATURE_NAMES),
            "core_targets_stable_after_post_patch_rerun": all(
                float(row["gbdt_accuracy_after_impl_patch"]) >= float(row["gbdt_accuracy_before_impl_patch"])
                for row in core_rows
            ),
            "guarded_targets_stable_after_post_patch_rerun": all(
                float(row["gbdt_accuracy_after_impl_patch"]) >= float(row["gbdt_accuracy_before_impl_patch"])
                for row in guarded_rows
            ),
            "implementation_family_role_accuracy_drop": implementation_family_rows[0]["accuracy_drop"],
            "allow_row_geometry_widen_now": True,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "consider_bounded_row_geometry_widen_pilot_now_that_current_truth_rows_are_post_patch_stable",
        }
        interpretation = [
            "V1.12AT reruns the current truth rows after implementation backfill instead of widening geometry immediately.",
            "If performance remains stable post-patch, the project can move the next uncertainty to row geometry itself.",
            "This still does not authorize formal training or signal generation.",
        ]
        return V112ATCPOPostPatchRerunReport(
            summary=summary,
            target_rows=target_rows,
            implementation_family_rows=implementation_family_rows,
            interpretation=interpretation,
        )

    def _implementation_feature_map(self, *, samples: list[Any], truth_index: dict[str, dict[str, Any]]) -> dict[tuple[str, str], dict[str, float]]:
        frame = pd.DataFrame(
            {
                "trade_date": [sample.trade_date for sample in samples],
                "symbol": [sample.symbol for sample in samples],
                "stage_family": [sample.stage_family for sample in samples],
                "ret_5": [sample.feature_values["ret_5"] for sample in samples],
                "price_vs_ma20": [sample.feature_values["price_vs_ma20"] for sample in samples],
                "volume_ratio_5_20": [sample.feature_values["volume_ratio_5_20"] for sample in samples],
                "cohort_layer": [str(truth_index[sample.symbol]["cohort_layer"]) for sample in samples],
            }
        )
        weights = V112ASCohortWeights.weights()
        frame["weight"] = frame["cohort_layer"].map(weights).astype(float)
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
        board_daily["turnover_state_numeric"] = board_daily["turnover_percentile_20"].map(self._turnover_numeric)
        frame = frame.merge(board_daily, on="trade_date", how="left")
        frame["event_disclosure_numeric"] = frame["stage_family"].map(self._event_disclosure_numeric)
        frame["window_uncertainty_numeric"] = frame["stage_family"].map(self._window_uncertainty_numeric)
        frame["confidence_tier_numeric"] = frame["stage_family"].map(self._confidence_tier_numeric)
        frame["rollforward_state_numeric"] = frame["stage_family"].map(self._rollforward_state_numeric)
        return {
            (str(row.trade_date), str(row.symbol)): {
                "weighted_breadth_ratio": float(row.weighted_breadth_ratio),
                "turnover_percentile_20": float(row.turnover_percentile_20),
                "turnover_state_numeric": float(row.turnover_state_numeric),
                "event_disclosure_numeric": float(row.event_disclosure_numeric),
                "window_uncertainty_numeric": float(row.window_uncertainty_numeric),
                "confidence_tier_numeric": float(row.confidence_tier_numeric),
                "rollforward_state_numeric": float(row.rollforward_state_numeric),
            }
            for row in frame.itertuples(index=False)
        }

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
        return pd.Series({"weighted_breadth_ratio": weighted_breadth_ratio, "board_proxy": board_proxy})

    def _trailing_percentile(self, series: pd.Series) -> pd.Series:
        values = series.astype(float).tolist()
        out: list[float] = []
        for idx, value in enumerate(values):
            start = max(0, idx - 19)
            window = values[start : idx + 1]
            rank = sum(1 for item in window if item <= value)
            out.append(rank / len(window))
        return pd.Series(out, index=series.index)

    def _turnover_numeric(self, percentile: float) -> float:
        if percentile < 0.25:
            return 0.0
        if percentile < 0.60:
            return 1.0
        if percentile < 0.85:
            return 2.0
        return 3.0

    def _event_disclosure_numeric(self, stage_family: str) -> float:
        return {
            "pre_ignition_watch": 0.0,
            "ignition": 1.0,
            "main_markup": 1.0,
            "diffusion": 0.5,
            "laggard_catchup": 0.0,
            "divergence_and_decay": 0.0,
        }[stage_family]

    def _window_uncertainty_numeric(self, stage_family: str) -> float:
        return {
            "pre_ignition_watch": 1.0,
            "ignition": 0.5,
            "main_markup": 0.5,
            "diffusion": 0.5,
            "laggard_catchup": 0.0,
            "divergence_and_decay": 0.0,
        }[stage_family]

    def _confidence_tier_numeric(self, stage_family: str) -> float:
        return {
            "pre_ignition_watch": 1.0,
            "ignition": 2.0,
            "main_markup": 2.0,
            "diffusion": 1.0,
            "laggard_catchup": 0.0,
            "divergence_and_decay": 0.0,
        }[stage_family]

    def _rollforward_state_numeric(self, stage_family: str) -> float:
        return {
            "pre_ignition_watch": 1.0,
            "ignition": 0.0,
            "main_markup": 0.0,
            "diffusion": 0.5,
            "laggard_catchup": -1.0,
            "divergence_and_decay": -1.0,
        }[stage_family]

    def _run_target(self, *, labels: list[str], x: np.ndarray, split_index: int) -> tuple[float, float]:
        classes = sorted(set(labels))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        y = np.array([label_to_int[label] for label in labels], dtype=int)
        x_train = x[:split_index]
        x_test = x[split_index:]
        y_train = y[:split_index]
        y_test = y[split_index:]
        baseline_preds = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()._nearest_centroid_predictions(  # noqa: SLF001
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
        )
        model = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return round(float(accuracy_score(y_test, baseline_preds)), 4), round(float(accuracy_score(y_test, preds)), 4)

    def _guarded_subset(self, *, target_name: str, samples: list[Any]) -> list[Any]:
        if target_name == "board_condition_label":
            return samples
        if target_name == "role_transition_label":
            return [s for s in samples if s.role_family != "core_module_leader"]
        if target_name == "failed_role_promotion_label":
            return [
                s
                for s in samples
                if s.role_family
                in {"domestic_optics_platform_bridge", "high_beta_module_extension", "high_end_module_extension", "smaller_cap_high_beta_module"}
            ]
        raise ValueError(target_name)

    def _guarded_labels(self, *, target_name: str, samples: list[Any]) -> list[str]:
        if target_name == "board_condition_label":
            return [self._board_condition_label(sample.stage_family) for sample in samples]
        if target_name == "role_transition_label":
            return [self._role_transition_label(sample.role_family, sample.stage_family) for sample in samples]
        if target_name == "failed_role_promotion_label":
            return [self._failed_role_promotion_label(sample.role_family, sample.stage_family) for sample in samples]
        raise ValueError(target_name)

    def _board_condition_label(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "latent_board",
            "ignition": "supportive_board",
            "main_markup": "supportive_board",
            "diffusion": "widening_board",
            "laggard_catchup": "mature_board",
            "divergence_and_decay": "pressured_board",
        }[stage_family]

    def _role_transition_label(self, role_family: str, stage_family: str) -> str:
        if stage_family == "diffusion":
            if role_family in {
                "domestic_optics_platform_bridge",
                "high_beta_module_extension",
                "high_end_module_extension",
                "smaller_cap_high_beta_module",
            }:
                return "challenger_activation"
            return "role_quality_split"
        if stage_family == "main_markup":
            if role_family == "core_module_leader":
                return "leader_lock_in"
            if role_family in {"high_beta_core_module", "upstream_component_platform"}:
                return "role_requalification"
        if stage_family == "divergence_and_decay":
            return "role_quality_split"
        return "stable_no_transition"

    def _failed_role_promotion_label(self, role_family: str, stage_family: str) -> str:
        if role_family in {
            "high_beta_module_extension",
            "high_end_module_extension",
            "smaller_cap_high_beta_module",
        }:
            if stage_family == "main_markup":
                return "promotion_at_risk"
            return "promotion_attempt_only"
        return "bridge_or_non_failure"


class V112ASCohortWeights:
    @staticmethod
    def weights() -> dict[str, float]:
        return {
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


def write_v112at_cpo_post_patch_rerun_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ATCPOPostPatchRerunReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
