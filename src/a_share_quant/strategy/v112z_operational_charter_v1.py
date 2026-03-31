from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZOperationalCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ZOperationalCharterAnalyzer:
    def analyze(
        self,
        *,
        protocol_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
        sidecar_v1_payload: dict[str, Any],
        gbdt_v2_payload: dict[str, Any],
    ) -> V112ZOperationalCharterReport:
        protocol_summary = dict(protocol_payload.get("summary", {}))
        if not bool(protocol_summary.get("foundation_ready_for_bounded_cycle_reconstruction")):
            raise ValueError("V1.12Z operational charter requires reconstruction readiness.")

        training_protocol = dict(training_protocol_payload.get("protocol", {}))
        sidecar_summary = dict(sidecar_v1_payload.get("summary", {}))
        gbdt_summary = dict(gbdt_v2_payload.get("summary", {}))

        charter = {
            "top_objective": (
                "Use bounded cycle reconstruction plus dual-track modeling to absorb one full CPO cycle as completely "
                "as possible, then translate the discovered mechanism back into owner-facing, auditable, no-leak research "
                "language before any downstream training rights are considered."
            ),
            "governing_principle": "black_box_discovers_white_box_constrains_narrative_validates",
            "three_layer_structure": {
                "cycle_reconstruction_layer": [
                    "reconstruct stage ordering across one bounded CPO cycle",
                    "reconstruct catalyst ordering and board chronology overlays",
                    "keep mixed-role and spillover ambiguity visible instead of over-cleaning it away",
                ],
                "black_box_absorption_layer": [
                    "use tabular black-box models to absorb heterogeneous and weakly structured information faster than linear-only baselines",
                    "treat the black-box layer as a mechanism finder rather than a truth legislator",
                    "require same-dataset and same-time-split comparisons against simpler baselines",
                ],
                "translation_and_audit_layer": [
                    "translate model discoveries into owner-facing cycle narrative",
                    "state which stage, role, catalyst, structure, or spillover mechanism the model appears to be capturing",
                    "reject any gain that cannot survive no-leak and audit review",
                ],
            },
            "model_stack": {
                "white_box_guardrail_baseline": {
                    "role": "audit_baseline_and_leak_detector",
                    "why": [
                        "keeps a minimum interpretable benchmark",
                        "makes stage-specific false-positive zones explicit",
                        "prevents black-box-only progress from becoming unauditable",
                    ],
                },
                "primary_black_box_family": {
                    "model": "hist_gradient_boosting_classifier",
                    "why": [
                        "currently best same-dataset sidecar result",
                        "robust on tabular heterogeneous features",
                        "low enough compute to support repeated bounded reruns",
                        "captures nonlinear interactions without requiring large sequence-scale data",
                    ],
                    "current_readout": {
                        "v1_test_accuracy": sidecar_summary.get("best_model_test_accuracy"),
                        "v2_test_accuracy": gbdt_summary.get("gbdt_v2_test_accuracy"),
                        "high_level_consolidation_false_positives_v2": gbdt_summary.get(
                            "gbdt_v2_high_level_consolidation_fp"
                        ),
                    },
                },
                "secondary_black_box_family": {
                    "model": "small_mlp_classifier",
                    "role": "nonlinear_comparison_model_not_primary_driver",
                    "why": [
                        "checks whether a different nonlinear family captures residual structure",
                        "should remain secondary until chronology and labels stabilize further",
                    ],
                },
                "deferred_model_families": [
                    "temporal_convolution_network",
                    "transformer_like_sequence_model",
                    "deeper_attention_based_sequence_family",
                ],
            },
            "immediate_success_criteria": [
                "produce a review-only reconstructed cycle map covering stage, catalyst, role, board chronology, and spillover overlays",
                "produce an owner-facing narrative reconstruction that can explain the cycle in time order and role order",
                "produce a black-box residual-mechanism memo that states what the black box sees beyond the guardrail baseline",
                "keep mixed-role entities, spillover candidates, and residual pending rows visible",
                "avoid any slide into auto training, auto label freeze, or auto signal logic",
            ],
            "narrative_acceptance_tests": [
                "time narration: explain what the market was seeing before ignition and why each major transition happened",
                "role narration: explain who acted as leader, mid-core, high-beta extension, branch extension, spillover, and weak-memory row",
                "catalyst narration: separate pre-visible catalysts, reinforcement catalysts, and post-hoc explanation noise",
                "structure narration: explain when the cycle was earnings-driven, board-driven, or mixed",
                "counterexample narration: explain which names looked core but should not be treated as true core",
                "trading-boundary narration: explain which windows look attackable, watch-only, or de-risking-only",
            ],
            "downstream_trading_objective": {
                "primary": "maximize return capture under drawdown control",
                "secondary": "improve profit_factor_and_risk_adjusted_participation",
                "must_not_replace": "no_leak_and_narrative_audit_requirements",
            },
            "no_leak_guardrails": [
                "time_split_only_no_random_shuffle",
                "all catalysts and events must be attached by point-in-time visibility",
                "no future-known role truth may be backfilled into earlier feature rows",
                "mixed-role, spillover, and pending rows must remain explicit instead of being silently deleted",
                "black-box output may not auto-legislate feature truth or label truth",
            ],
            "recommended_next_chain": [
                "run_v112z_bounded_cycle_reconstruction_pass",
                "freeze_bounded_cpo_cohort_map_and_labeling_pilot",
                "run_dual_track_guardrail_vs_black_box_benchmark",
                "write_black_box_residual_mechanism_memo",
                "review_return_drawdown_profit_factor_before_any_training_rights_change",
            ],
            "training_protocol_reference": {
                "sample_unit": training_protocol.get("sample_unit"),
                "feature_block_count": len(dict(training_protocol.get("feature_blocks", {}))),
                "label_count": len(list(training_protocol.get("label_set", []))),
            },
        }

        summary = {
            "acceptance_posture": "freeze_v112z_operational_charter_v1",
            "cycle_absorption_is_primary_objective": True,
            "black_box_primary_family": "hist_gradient_boosting_classifier",
            "white_box_role": "guardrail_and_audit_baseline",
            "owner_facing_narrative_required": True,
            "formal_training_still_forbidden": True,
            "ready_for_reconstruction_pass": True,
        }

        interpretation = [
            "The highest current priority is cycle absorption, not early explainable-feature completeness.",
            "Black-box models are allowed to lead discovery, but they remain bounded by no-leak rules, white-box guardrails, and owner-facing narrative audit.",
            "V1.12Z should be judged not only by predictive deltas but by whether the cycle can be reconstructed and verbally explained in a stable, auditable way.",
        ]
        return V112ZOperationalCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112z_operational_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZOperationalCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
