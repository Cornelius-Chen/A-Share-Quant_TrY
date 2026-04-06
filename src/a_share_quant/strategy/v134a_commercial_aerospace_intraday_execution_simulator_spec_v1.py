from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ACommercialAerospaceIntradayExecutionSimulatorSpecReport:
    summary: dict[str, Any]
    simulator_rows: list[dict[str, Any]]
    action_rows: list[dict[str, Any]]
    cost_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "simulator_rows": self.simulator_rows,
            "action_rows": self.action_rows,
            "cost_rows": self.cost_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V134ACommercialAerospaceIntradayExecutionSimulatorSpecAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.build_protocol_path = (
            repo_root / "reports" / "analysis" / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        )
        self.action_ladder_path = (
            repo_root / "reports" / "analysis" / "v132s_commercial_aerospace_intraday_override_action_ladder_v1.json"
        )
        self.phase_1_triage_path = (
            repo_root / "reports" / "analysis" / "v133z_commercial_aerospace_yz_all_session_visibility_triage_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_execution_simulator_spec_v1.csv"
        )

    def analyze(self) -> V134ACommercialAerospaceIntradayExecutionSimulatorSpecReport:
        build_protocol = json.loads(self.build_protocol_path.read_text(encoding="utf-8"))
        action_ladder = json.loads(self.action_ladder_path.read_text(encoding="utf-8"))
        phase_1 = json.loads(self.phase_1_triage_path.read_text(encoding="utf-8"))

        simulator_rows = [
            {
                "component": "trigger_evaluation_clock",
                "policy": "minute_close_only",
                "detail": "all minute-tier triggers are evaluated only after the current 1min bar closes",
            },
            {
                "component": "earliest_fill_policy",
                "policy": "next_bar_open_only",
                "detail": "a trigger fired on minute t may fill no earlier than the next visible minute open",
            },
            {
                "component": "fill_price_reference",
                "policy": "next_bar_open_plus_slippage",
                "detail": "fills use the next minute open with fixed bps slippage applied in the adverse direction",
            },
            {
                "component": "execution_lane_scope",
                "policy": "canonical_seed_sessions_first",
                "detail": "phase 2 starts on the canonical six seed sessions before any broader session simulation is allowed",
            },
            {
                "component": "position_mutation_boundary",
                "policy": "intraday_shadow_read_only_relative_to_eod_primary",
                "detail": "the simulator may read frozen EOD positions as starting state but may not mutate the authoritative EOD primary outputs",
            },
            {
                "component": "same_session_readd_guardrail",
                "policy": "blocked_after_severe_and_cooldown_after_reversal",
                "detail": "severe exits forbid same-session re-add; reversal-triggered de-risk opens a cooldown-only no-readd watch for the rest of the audited window",
            },
        ]

        action_rows = [
            {
                "minute_tier_label": "severe_override_positive",
                "governance_action": "emergency_exit_shadow_override",
                "trigger_eval_ts": "bar_close_t",
                "fill_ts": "open_t_plus_1",
                "position_effect": "sell_100_percent_of_remaining_position",
                "same_session_readd": "forbidden",
            },
            {
                "minute_tier_label": "reversal_watch",
                "governance_action": "panic_derisk_watch",
                "trigger_eval_ts": "bar_close_t",
                "fill_ts": "open_t_plus_1",
                "position_effect": "sell_50_percent_of_remaining_position",
                "same_session_readd": "cooldown_for_rest_of_window",
            },
            {
                "minute_tier_label": "mild_override_watch",
                "governance_action": "do_not_readd_watch",
                "trigger_eval_ts": "bar_close_t",
                "fill_ts": "no_immediate_trade",
                "position_effect": "hold_position_but_block_incremental_readd",
                "same_session_readd": "forbidden",
            },
        ]

        ladder_map = {
            row["minute_tier_label"]: row["governance_action"] for row in action_ladder["action_rows"]
        }
        for row in action_rows:
            row["ladder_consistency"] = row["governance_action"] == ladder_map.get(row["minute_tier_label"])

        cost_rows = [
            {
                "cost_item": "commission_rate",
                "value": 0.0003,
                "unit": "fraction",
                "detail": "matched to the frozen commercial-aerospace lawful EOD primary cost baseline",
            },
            {
                "cost_item": "min_commission",
                "value": 5.0,
                "unit": "cny",
                "detail": "minimum per-order commission floor",
            },
            {
                "cost_item": "sell_stamp_tax_rate",
                "value": 0.001,
                "unit": "fraction",
                "detail": "applies only to sell-side minute fills",
            },
            {
                "cost_item": "slippage_bps",
                "value": 5.0,
                "unit": "bps",
                "detail": "applied in the adverse direction against the simulated fill price",
            },
        ]

        acceptance_rows = [
            {
                "acceptance_item": "phase_1_complete_prerequisite",
                "status": "required",
                "detail": phase_1["summary"]["authoritative_status"],
            },
            {
                "acceptance_item": "same_bar_future_knowledge_impossible",
                "status": "required",
                "detail": "trigger evaluation at minute-close and fill at next-bar open prohibit same-bar trading on incomplete information",
            },
            {
                "acceptance_item": "seed_session_reproducibility",
                "status": "required",
                "detail": "all six canonical seed sessions must produce deterministic trigger and fill rows when rerun",
            },
            {
                "acceptance_item": "position_and_cash_conservation",
                "status": "required",
                "detail": "minute fills must conserve signed position quantity, cash, and cost accounting independently from the frozen EOD lane",
            },
            {
                "acceptance_item": "phase_3_still_blocked",
                "status": "required",
                "detail": "the simulator spec does not authorize replay-lane binding or promotion into the authoritative EOD primary",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(action_rows[0].keys()))
            writer.writeheader()
            writer.writerows(action_rows)

        summary = {
            "acceptance_posture": "build_v134a_commercial_aerospace_intraday_execution_simulator_spec_v1",
            "upstream_workstream": build_protocol["workstream_rows"][1]["workstream"],
            "phase_1_status": phase_1["summary"]["authoritative_status"],
            "simulator_component_count": len(simulator_rows),
            "action_mapping_count": len(action_rows),
            "cost_item_count": len(cost_rows),
            "acceptance_item_count": len(acceptance_rows),
            "spec_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_execution_simulator_spec_ready_for_phase_2_triage",
        }
        interpretation = [
            "V1.34A converts the blocked phase-2 lane into an explicit minute-execution simulator specification.",
            "The spec stays narrow: it defines trigger timing, fill timing, action sizing, cost treatment, and no-readd guardrails for a shadow-only intraday lane.",
        ]
        return V134ACommercialAerospaceIntradayExecutionSimulatorSpecReport(
            summary=summary,
            simulator_rows=simulator_rows,
            action_rows=action_rows,
            cost_rows=cost_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ACommercialAerospaceIntradayExecutionSimulatorSpecReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ACommercialAerospaceIntradayExecutionSimulatorSpecAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134a_commercial_aerospace_intraday_execution_simulator_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
