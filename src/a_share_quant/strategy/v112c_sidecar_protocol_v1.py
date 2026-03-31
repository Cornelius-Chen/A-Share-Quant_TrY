from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CSidecarProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CSidecarProtocolAnalyzer:
    """Freeze the first report-only black-box sidecar comparison rules."""

    def analyze(
        self,
        *,
        hotspot_review_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
    ) -> V112CSidecarProtocolReport:
        hotspot_summary = dict(hotspot_review_payload.get("summary", {}))
        protocol_summary = dict(training_protocol_payload.get("summary", {}))
        if not bool(hotspot_summary.get("ready_for_sidecar_protocol_next")):
            raise ValueError("V1.12C sidecar protocol requires the hotspot review first.")
        if str(protocol_summary.get("acceptance_posture")) != "freeze_v112_training_protocol_v1":
            raise ValueError("V1.12C sidecar protocol must inherit the frozen V1.12 training grammar.")

        protocol = {
            "comparison_goal": "reduce_optimistic_false_positives_in_late_markup_and_high_level_consolidation",
            "same_dataset_rule": "reuse_v112b_first_trainable_pilot_dataset_without_object_widening",
            "same_label_rule": "reuse_forward_return_bucket_max_drawdown_bucket_and_carry_outcome_class",
            "validation_rule": "keep_the_same_time_split_as_v112b_no_random_shuffle",
            "candidate_model_families": [
                "hist_gradient_boosting_classifier",
                "small_mlp_classifier",
            ],
            "must_report_metrics": [
                "test_accuracy",
                "carry_constructive_precision",
                "carry_constructive_recall",
                "false_positive_count_in_major_markup",
                "false_positive_count_in_high_level_consolidation",
            ],
            "hard_boundaries": [
                "report_only_sidecar_only",
                "no_strategy_integration",
                "no_intraday_features",
                "no_dataset_widening",
                "no_black_box_deployment_even_if_sidecar_outperforms",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v112c_sidecar_protocol_v1",
            "candidate_model_family_count": len(protocol["candidate_model_families"]),
            "metric_count": len(protocol["must_report_metrics"]),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The first sidecar is constrained to the exact same dataset and labels so model comparison does not get confounded with data changes.",
            "The comparison target is explicit: reduce optimistic false positives in the baseline's known hotspot stages.",
            "Even an improved sidecar remains report-only until a later phase explicitly reviews its evidence.",
        ]
        return V112CSidecarProtocolReport(summary=summary, protocol=protocol, interpretation=interpretation)


def write_v112c_sidecar_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CSidecarProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
