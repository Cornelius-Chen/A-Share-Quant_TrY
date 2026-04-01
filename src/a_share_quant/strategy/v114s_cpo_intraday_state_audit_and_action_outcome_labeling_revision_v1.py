from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionReport:
    summary: dict[str, Any]
    board_state_layer_rows: list[dict[str, Any]]
    must_have_rows: list[dict[str, Any]]
    should_have_rows: list[dict[str, Any]]
    action_outcome_label_rows: list[dict[str, Any]]
    current_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "board_state_layer_rows": self.board_state_layer_rows,
            "must_have_rows": self.must_have_rows,
            "should_have_rows": self.should_have_rows,
            "action_outcome_label_rows": self.action_outcome_label_rows,
            "current_gap_rows": self.current_gap_rows,
            "interpretation": self.interpretation,
        }


class V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionReport:
        raw_root = self.repo_root / "data" / "raw"
        intraday_files = [
            path
            for path in raw_root.rglob("*")
            if path.is_file() and ("minute" in path.name.lower() or "intraday" in path.name.lower())
        ]

        board_state_layer_rows = [
            {
                "layer_name": "diffusion_authenticity",
                "question_answered": "Is board expansion being led by core strength or by noisy tail dispersion?",
                "why_it_is_primary": "The project objective is to capture diffusion-style main-uptrend boards, not generic single-name momentum.",
                "example_intraday_proxies": [
                    "leader_vs_tail_relative_return",
                    "core_turnover_share",
                    "intraday_breadth",
                    "tail_chase_ratio",
                ],
            },
            {
                "layer_name": "main_uptrend_persistence",
                "question_answered": "Is intraday strength sustaining into the close and likely to persist, or only flashing briefly?",
                "why_it_is_primary": "Add sizing should respond to persistence of edge, not to isolated hot bars.",
                "example_intraday_proxies": [
                    "late_session_close_quality",
                    "vwap_reclaim_persistence",
                    "afternoon_strength_retention",
                    "post_catalyst_follow_through",
                ],
            },
            {
                "layer_name": "board_risk_off_and_decay",
                "question_answered": "Is the board as a whole entering an internally fragile or decaying state?",
                "why_it_is_primary": "Drawdown control in a diffusion board is often a board-level decay problem before it becomes a single-name failure.",
                "example_intraday_proxies": [
                    "failed_push_sequence",
                    "breadth_fade_into_close",
                    "board_limit_break_rate",
                    "core_to_tail_flow_deterioration",
                ],
            },
            {
                "layer_name": "role_migration",
                "question_answered": "Are leader, core, sidecar, and tail roles strengthening in a healthy order or deforming into unstable migration?",
                "why_it_is_primary": "A true diffusion main-uptrend board rotates expression without losing core sponsorship.",
                "example_intraday_proxies": [
                    "leader_strength_acceleration",
                    "core_vs_sidecar_share_shift",
                    "role_rank_persistence",
                    "new_tail_surge_without_core_support",
                ],
            },
            {
                "layer_name": "single_name_action_confirmation",
                "question_answered": "Given a board state, is this specific symbol's add/reduce/close action getting cleaner confirmation?",
                "why_it_is_primary": "Single-name confirmation remains necessary, but now sits under the board-state audit instead of replacing it.",
                "example_intraday_proxies": [
                    "reclaim_after_break",
                    "volume_price_quality",
                    "relative_intraday_leadership",
                ],
            },
        ]

        must_have_rows = [
            {
                "field_group": "intraday_bars_with_session_anchors",
                "fields": [
                    "trade_date",
                    "symbol",
                    "bar_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "turnover",
                    "pre_close",
                    "intraday_vwap",
                    "session_high",
                    "session_low",
                ],
                "why_needed": "Without anchors, reclaim-versus-fail and close-quality factors are too fuzzy to train cleanly.",
            },
            {
                "field_group": "float_and_turnover_rate",
                "fields": [
                    "float_shares",
                    "free_float_market_cap",
                    "daily_turnover_rate",
                    "intraday_turnover_rate_proxy",
                ],
                "why_needed": "Turnover amount alone cannot compare heat across large-core names and smaller extension names.",
            },
            {
                "field_group": "board_relative_intraday_reference",
                "fields": [
                    "leader_basket_intraday",
                    "core_basket_intraday",
                    "tail_basket_intraday",
                    "intraday_breadth",
                    "advance_ratio",
                    "relative_to_board_avg_return_intraday",
                    "relative_to_core_leader_intraday",
                ],
                "why_needed": "The model must distinguish healthy core-led diffusion from noisy tail-led extension.",
            },
            {
                "field_group": "tradability_and_session_state",
                "fields": [
                    "limit_up_state",
                    "limit_down_state",
                    "halt_state",
                    "auction_session_flag",
                    "continuous_session_flag",
                    "bar_tradability_flag",
                ],
                "why_needed": "A board can look strong while the actual symbol or bar is not executable for confirmation-driven adds or exits.",
            },
            {
                "field_group": "catalyst_timestamp_alignment",
                "fields": [
                    "event_time",
                    "event_type",
                    "post_event_window_marker",
                ],
                "why_needed": "Without catalyst timing, intraday reinforcement can be misread as pure technical follow-through.",
            },
        ]

        should_have_rows = [
            {
                "field_group": "index_and_etf_context",
                "fields": [
                    "ChiNext_intraday",
                    "STAR_intraday",
                    "communication_etf_intraday",
                    "sector_etf_relative_move",
                ],
                "why_needed": "Useful for validating whether board strength is internally generated or just drifting with the broader complex.",
            },
            {
                "field_group": "board_internal_flow_snapshot",
                "fields": [
                    "top3_core_turnover_intraday",
                    "core_vs_tail_turnover_share",
                    "tail_extension_heat_ratio",
                ],
                "why_needed": "Helpful for measuring role migration and concentration shifts with finer granularity.",
            },
            {
                "field_group": "micro_liquidity_proxy",
                "fields": [
                    "best_bid_ask_proxy",
                    "estimated_slippage_band",
                ],
                "why_needed": "Improves execution realism once the state-audit and action-label loop is already stable.",
            },
        ]

        action_outcome_label_rows = [
            {
                "action_name": "entry",
                "label_family": "conditional_expectancy",
                "required_labels": [
                    "P_entry_forward_gain_1d",
                    "P_entry_forward_gain_3d",
                    "P_entry_forward_gain_5d",
                    "P_entry_adverse_move_3d",
                ],
                "why_needed": "Entry must stay distinct from add; participation is allowed before acceleration is fully confirmed.",
            },
            {
                "action_name": "add",
                "label_family": "expectancy_revision_up",
                "required_labels": [
                    "P_add_forward_gain_1d",
                    "P_add_forward_gain_3d",
                    "P_add_forward_gain_5d",
                    "P_add_adverse_move_1d",
                    "P_add_adverse_move_3d",
                    "add_expectancy_uplift_vs_hold",
                ],
                "why_needed": "Add should mean future upside probability is revised up and downside probability is revised down, not merely that structure looks stronger.",
            },
            {
                "action_name": "reduce",
                "label_family": "expectancy_revision_down",
                "required_labels": [
                    "P_reduce_avoided_drawdown_1d",
                    "P_reduce_avoided_drawdown_3d",
                    "P_reduce_missed_upside_3d",
                    "reduce_payoff_decay_vs_hold",
                ],
                "why_needed": "Reduce should reflect worsening expected payoff quality before full invalidation.",
            },
            {
                "action_name": "close",
                "label_family": "invalidation_realization",
                "required_labels": [
                    "P_close_invalidation_realized_1d",
                    "P_close_invalidation_realized_3d",
                    "P_close_opportunity_cost_3d",
                ],
                "why_needed": "Close must be judged against both avoided loss and surrendered continuation.",
            },
            {
                "action_name": "board_risk_off",
                "label_family": "board_state_protection",
                "required_labels": [
                    "P_board_risk_off_follow_through_1d",
                    "P_board_risk_off_follow_through_3d",
                    "P_core_to_tail_deterioration_1d",
                ],
                "why_needed": "The project objective includes board-level drawdown containment, not only single-name timing.",
            },
        ]

        current_gap_rows = [
            {
                "gap_name": "no_intraday_raw_bars_present",
                "current_status": "missing",
                "impact": "No board-state intraday audit or action-outcome labeling can run yet.",
                "evidence": f"intraday_file_count={len(intraday_files)}",
            },
            {
                "gap_name": "float_and_turnover_rate_not_available",
                "current_status": "missing",
                "impact": "Cross-symbol heat and churn are not comparable enough for robust add/reduce learning.",
                "evidence": "security_master lacks float shares / free-float market cap fields",
            },
            {
                "gap_name": "board_relative_intraday_baskets_missing",
                "current_status": "missing",
                "impact": "Cannot yet tell healthy core-led diffusion from noisy tail-led expansion.",
                "evidence": "no leader/core/tail intraday basket files are present",
            },
            {
                "gap_name": "tradability_state_missing",
                "current_status": "missing",
                "impact": "Confirmation may still confuse visual strength with executable strength.",
                "evidence": "no bar-level limit/halt/session flags available in intraday inputs",
            },
            {
                "gap_name": "action_outcome_labels_not_defined_in_data_pipeline",
                "current_status": "missing",
                "impact": "Training remains structure-confirmation heavy instead of expectancy-semantics heavy.",
                "evidence": "no intraday action-outcome label table exists yet",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_v1",
            "research_objective": "maximize_capture_of_diffusion_style_main_uptrend_while_containing_unnecessary_drawdown",
            "protocol_upgrade": "intraday_confirmation_protocol_to_intraday_state_audit_and_action_outcome_labeling_protocol",
            "board_state_layer_count": len(board_state_layer_rows),
            "must_have_group_count": len(must_have_rows),
            "action_outcome_label_family_count": len(action_outcome_label_rows),
            "intraday_feed_ready_now": False,
            "recommended_next_posture": "collect_narrow_intraday_state_audit_fields_and_define_action_outcome_label_table_before_any_intraday_learning_run",
        }

        interpretation = [
            "V1.14S widens the target from narrow add/reduce confirmation to intraday state audit for diffusion-style main-uptrend boards.",
            "The key upgrade is not just more fields; it is the addition of action-outcome labels so add/reduce/close can be trained as expectancy revisions rather than stronger-structure proxies.",
            "The first intraday build should stay narrow in symbol scope, but broad in state scope: board diffusion authenticity, persistence, decay risk, role migration, and single-name confirmation must all be observable.",
        ]

        return V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionReport(
            summary=summary,
            board_state_layer_rows=board_state_layer_rows,
            must_have_rows=must_have_rows,
            should_have_rows=should_have_rows,
            action_outcome_label_rows=action_outcome_label_rows,
            current_gap_rows=current_gap_rows,
            interpretation=interpretation,
        )


def write_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
