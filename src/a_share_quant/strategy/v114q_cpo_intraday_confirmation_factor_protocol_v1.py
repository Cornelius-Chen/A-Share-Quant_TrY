from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114QCpoIntradayConfirmationFactorProtocolReport:
    summary: dict[str, Any]
    target_object_rows: list[dict[str, Any]]
    intraday_factor_rows: list[dict[str, Any]]
    action_mapping_rows: list[dict[str, Any]]
    readiness_audit: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_object_rows": self.target_object_rows,
            "intraday_factor_rows": self.intraday_factor_rows,
            "action_mapping_rows": self.action_mapping_rows,
            "readiness_audit": self.readiness_audit,
            "interpretation": self.interpretation,
        }


class V114QCpoIntradayConfirmationFactorProtocolAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V114QCpoIntradayConfirmationFactorProtocolReport:
        raw_root = self.repo_root / "data" / "raw"
        intraday_files = [
            path
            for path in raw_root.rglob("*")
            if path.is_file() and ("minute" in path.name.lower() or "intraday" in path.name.lower())
        ]

        target_object_rows = [
            {
                "symbol": "300308",
                "object_family": "core_module_leader",
                "why_selected": "Holding-veto and add timing both matter; core leader is the cleanest main-uptrend confirmation object.",
                "priority": "highest",
            },
            {
                "symbol": "300502",
                "object_family": "high_beta_core_module",
                "why_selected": "Needs cleaner de-risk versus continuation separation during strong-board extension days.",
                "priority": "highest",
            },
            {
                "symbol": "300757",
                "object_family": "packaging_process_enabler",
                "why_selected": "Admission/add windows exist, but daily confirmation is now exhausted and needs intraday quality checks.",
                "priority": "high",
            },
            {
                "symbol": "688498",
                "object_family": "laser_chip_component",
                "why_selected": "Eligibility-only line; intraday should remain secondary here and used only after the three stronger action names.",
                "priority": "medium",
            },
        ]

        intraday_factor_rows = [
            {
                "factor_name": "reclaim_after_break",
                "factor_family": "washout_vs_distribution",
                "factor_definition": "After breaking intraday VWAP / session anchor, measure whether price reclaims the level quickly with improving turnover.",
                "why_it_matters_for_diffusion_main_markup": "Constructive shakeouts in a real diffusion main-uptrend often reclaim structure; distribution days stay below and degrade.",
                "serves_action": ["add_confirmation", "reduce_confirmation"],
            },
            {
                "factor_name": "volume_price_quality",
                "factor_family": "continuation_quality",
                "factor_definition": "Distinguish upward expansion with price follow-through from high turnover with stalled price progress.",
                "why_it_matters_for_diffusion_main_markup": "The project now needs to know whether stronger board days still represent profitable extension or already-fragile churn.",
                "serves_action": ["add_confirmation"],
            },
            {
                "factor_name": "late_session_close_quality",
                "factor_family": "close_quality",
                "factor_definition": "Evaluate whether the symbol closes back near the intraday strength zone or fades into the close.",
                "why_it_matters_for_diffusion_main_markup": "A real main-uptrend diffusion leg usually preserves close quality; fading closes are often where daily-only add logic overcommits.",
                "serves_action": ["add_confirmation", "reduce_confirmation", "holding_veto_confirmation"],
            },
            {
                "factor_name": "relative_intraday_leadership",
                "factor_family": "relative_structure",
                "factor_definition": "Measure whether the symbol strengthens intraday relative to the board's other core names and to the communication / optical ETF proxy.",
                "why_it_matters_for_diffusion_main_markup": "The target is not generic momentum; it is expansion inside an already-diffusing main-uptrend board.",
                "serves_action": ["add_confirmation", "re_add_confirmation"],
            },
            {
                "factor_name": "intraday_concentration_shift",
                "factor_family": "board_internal_flow",
                "factor_definition": "Track whether incremental turnover is concentrating back into core names or dispersing toward fragile tails.",
                "why_it_matters_for_diffusion_main_markup": "Core concentration strengthening supports add; noisy tail dispersion warns that the day may be broad but low quality.",
                "serves_action": ["add_confirmation", "board_level_risk_off_watch"],
            },
            {
                "factor_name": "failed_push_sequence",
                "factor_family": "distribution_warning",
                "factor_definition": "Detect repeated intraday push attempts that make less price progress while using more turnover.",
                "why_it_matters_for_diffusion_main_markup": "This is the practical intraday proxy for 'future upside probability stops improving'.",
                "serves_action": ["reduce_confirmation", "holding_veto_confirmation"],
            },
        ]

        action_mapping_rows = [
            {
                "action_name": "entry",
                "expectancy_semantics": "Worth participating, but not yet a proven acceleration confirmation.",
                "intraday_need_level": "secondary",
                "reading": "Daily board-state and role-state still do most of the work here.",
            },
            {
                "action_name": "add",
                "expectancy_semantics": "Future winning probability is being revised up while downside probability is being revised down.",
                "intraday_need_level": "primary",
                "reading": "This is the main reason to add intraday now.",
            },
            {
                "action_name": "reduce",
                "expectancy_semantics": "Future upside probability is weakening or payoff quality is decaying, but the line is not fully invalid yet.",
                "intraday_need_level": "primary",
                "reading": "Daily information got us close, but this is where same-day quality matters.",
            },
            {
                "action_name": "holding_veto",
                "expectancy_semantics": "Invalidation probability dominates continuation probability.",
                "intraday_need_level": "supporting",
                "reading": "Hard veto remains daily-first, with intraday used for timing confirmation rather than rewriting the veto.",
            },
        ]

        readiness_audit = {
            "intraday_files_present_now": len(intraday_files) > 0,
            "intraday_file_count": len(intraday_files),
            "intraday_feed_ready_now": False,
            "blocking_reason": "No minute/intraday raw files are present under data/raw yet.",
            "minimum_build_scope": [
                "300308",
                "300502",
                "300757",
                "688498",
            ],
            "minimum_required_fields": [
                "symbol",
                "trade_date",
                "bar_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
            ],
            "teaching_boundary": "Intraday is not for generic alpha mining; it is only for confirming add/reduce quality inside diffusion-style main-uptrend board states.",
        }

        summary = {
            "acceptance_posture": "freeze_v114q_cpo_intraday_confirmation_factor_protocol_v1",
            "target_board_style": "diffusion_main_uptrend_board",
            "target_use_case": "narrow_intraday_confirmation_for_add_reduce_not_general_intraday_trading",
            "target_object_count": len(target_object_rows),
            "intraday_factor_count": len(intraday_factor_rows),
            "intraday_feed_ready_now": readiness_audit["intraday_feed_ready_now"],
            "recommended_next_posture": "collect_narrow_intraday_bars_for_mature_cpo_action_names_before_any_intraday_replay_attempt",
        }
        interpretation = [
            "V1.14Q narrows the intraday question to the real unresolved layer: confirmation for add/reduce inside a diffusion-style main-uptrend board.",
            "This protocol deliberately avoids generic intraday alpha mining. It only supports action-quality confirmation where the daily layer has already been exhausted.",
            "The current repository does not yet contain raw intraday bars, so the next step is data collection for a very small symbol set, not immediate intraday replay.",
        ]

        return V114QCpoIntradayConfirmationFactorProtocolReport(
            summary=summary,
            target_object_rows=target_object_rows,
            intraday_factor_rows=intraday_factor_rows,
            action_mapping_rows=action_mapping_rows,
            readiness_audit=readiness_audit,
            interpretation=interpretation,
        )


def write_v114q_cpo_intraday_confirmation_factor_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114QCpoIntradayConfirmationFactorProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114QCpoIntradayConfirmationFactorProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_v114q_cpo_intraday_confirmation_factor_protocol_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114q_cpo_intraday_confirmation_factor_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
