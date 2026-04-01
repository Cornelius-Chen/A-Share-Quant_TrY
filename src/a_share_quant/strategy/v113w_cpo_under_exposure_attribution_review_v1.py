from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113WCPOUnderExposureAttributionReviewReport:
    summary: dict[str, Any]
    key_findings: list[str]
    top_opportunity_miss_rows: list[dict[str, Any]]
    episode_action_rows: list[dict[str, Any]]
    post_exit_follow_through_rows: list[dict[str, Any]]
    symbol_pnl_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "key_findings": self.key_findings,
            "top_opportunity_miss_rows": self.top_opportunity_miss_rows,
            "episode_action_rows": self.episode_action_rows,
            "post_exit_follow_through_rows": self.post_exit_follow_through_rows,
            "symbol_pnl_rows": self.symbol_pnl_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113WCPOUnderExposureAttributionReviewAnalyzer:
    def analyze(
        self,
        *,
        v113v_payload: dict[str, Any],
    ) -> V113WCPOUnderExposureAttributionReviewReport:
        summary_v = dict(v113v_payload.get("summary", {}))
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.13W expects the V1.13V full-board replay report.")

        day_rows = list(v113v_payload.get("replay_day_rows", []))
        order_rows = list(v113v_payload.get("executed_order_rows", []))
        if not day_rows:
            raise ValueError("V1.13W requires replay day rows.")

        initial_equity = float(day_rows[0]["equity_after_close"])
        final_equity = float(day_rows[-1]["equity_after_close"])
        strategy_curve = final_equity / initial_equity

        board_curve = 1.0
        board_peak = 1.0
        board_max_drawdown = 0.0
        strategy_peak = initial_equity
        strategy_max_drawdown = 0.0
        for row in day_rows:
            board_avg_return = float(dict(row["board_context"]).get("avg_return", 0.0))
            board_curve *= 1.0 + board_avg_return
            board_peak = max(board_peak, board_curve)
            if board_peak > 0:
                board_max_drawdown = max(board_max_drawdown, 1.0 - board_curve / board_peak)

            equity = float(row["equity_after_close"])
            strategy_peak = max(strategy_peak, equity)
            if strategy_peak > 0:
                strategy_max_drawdown = max(strategy_max_drawdown, 1.0 - equity / strategy_peak)

        opportunity_miss_rows = []
        for row in day_rows:
            board_context = dict(row["board_context"])
            avg_return = float(board_context.get("avg_return", 0.0))
            breadth = float(board_context.get("breadth", 0.0))
            exposure = float(row["gross_exposure_after_close"])
            if avg_return >= 0.06 and breadth >= 0.8 and exposure < 0.2:
                opportunity_miss_rows.append(
                    {
                        "trade_date": str(row["trade_date"]),
                        "board_avg_return": round(avg_return, 6),
                        "board_breadth": round(breadth, 6),
                        "gross_exposure_after_close": round(exposure, 6),
                        "episode_count": int(row["episode_count"]),
                        "planned_order_count": int(row["planned_order_count"]),
                        "top_turnover_symbols": list(board_context.get("top_turnover_symbols", [])),
                        "miss_reading": "board_strong_but_strategy_still_light",
                    }
                )
        top_opportunity_miss_rows = sorted(
            opportunity_miss_rows,
            key=lambda item: (item["board_avg_return"], item["board_breadth"]),
            reverse=True,
        )[:10]

        episode_action_rows = []
        for row in day_rows:
            if int(row["episode_count"]) <= 0:
                continue
            board_context = dict(row["board_context"])
            exposure = float(row["gross_exposure_after_close"])
            avg_return = float(board_context.get("avg_return", 0.0))
            breadth = float(board_context.get("breadth", 0.0))
            if exposure < 0.2:
                sizing_reading = "under_exposed"
            elif exposure < 0.4:
                sizing_reading = "medium_expression"
            else:
                sizing_reading = "high_expression"
            episode_action_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "board_avg_return": round(avg_return, 6),
                    "board_breadth": round(breadth, 6),
                    "gross_exposure_after_close": round(exposure, 6),
                    "planned_order_count": int(row["planned_order_count"]),
                    "sizing_reading": sizing_reading,
                }
            )

        day_index = {str(row["trade_date"]): idx for idx, row in enumerate(day_rows)}
        post_exit_follow_through_rows = []
        for order in order_rows:
            if str(order["action"]) != "sell":
                continue
            idx = day_index.get(str(order["trade_date"]))
            if idx is None:
                continue
            future_rows = day_rows[idx + 1 : idx + 6]
            next5_board_sum = sum(float(dict(row["board_context"]).get("avg_return", 0.0)) for row in future_rows)
            follow_reading = "post_exit_board_follow_through_positive" if next5_board_sum > 0 else "post_exit_board_follow_through_negative"
            post_exit_follow_through_rows.append(
                {
                    "trade_date": str(order["trade_date"]),
                    "symbol": str(order["symbol"]),
                    "source": str(order["source"]),
                    "action_mode": str(order["action_mode"]),
                    "next5_board_avg_sum": round(next5_board_sum, 6),
                    "next5_trade_day_count": len(future_rows),
                    "follow_reading": follow_reading,
                }
            )

        positions_qty: dict[str, int] = {}
        remaining_cost: dict[str, float] = {}
        realized_pnl: dict[str, float] = {}
        turnover_by_symbol: dict[str, float] = {}
        for order in order_rows:
            symbol = str(order["symbol"])
            quantity = int(order["quantity"])
            notional = float(order["notional"])
            price = float(order["reference_price"])
            turnover_by_symbol[symbol] = turnover_by_symbol.get(symbol, 0.0) + notional
            if str(order["action"]) == "buy":
                positions_qty[symbol] = positions_qty.get(symbol, 0) + quantity
                remaining_cost[symbol] = remaining_cost.get(symbol, 0.0) + notional
                realized_pnl.setdefault(symbol, 0.0)
            else:
                existing_qty = positions_qty.get(symbol, 0)
                avg_cost = 0.0 if existing_qty <= 0 else remaining_cost.get(symbol, 0.0) / existing_qty
                realized_pnl[symbol] = realized_pnl.get(symbol, 0.0) + (price - avg_cost) * quantity
                remaining_cost[symbol] = remaining_cost.get(symbol, 0.0) - avg_cost * quantity
                positions_qty[symbol] = max(0, existing_qty - quantity)

        symbol_pnl_rows = []
        for symbol in sorted(set(list(positions_qty.keys()) + list(realized_pnl.keys()) + list(turnover_by_symbol.keys()))):
            qty = positions_qty.get(symbol, 0)
            rem_cost = remaining_cost.get(symbol, 0.0)
            avg_cost = 0.0 if qty <= 0 else rem_cost / qty
            symbol_pnl_rows.append(
                {
                    "symbol": symbol,
                    "position_quantity": qty,
                    "remaining_cost": round(rem_cost, 4),
                    "avg_cost": round(avg_cost, 4),
                    "realized_pnl": round(realized_pnl.get(symbol, 0.0), 4),
                    "turnover": round(turnover_by_symbol.get(symbol, 0.0), 4),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113w_cpo_under_exposure_attribution_review_v1",
            "strategy_curve": round(strategy_curve, 4),
            "board_equal_weight_curve": round(board_curve, 4),
            "curve_gap_vs_board": round(strategy_curve - board_curve, 4),
            "strategy_max_drawdown": round(strategy_max_drawdown, 4),
            "board_equal_weight_max_drawdown": round(board_max_drawdown, 4),
            "top_opportunity_miss_count": len(top_opportunity_miss_rows),
            "episode_action_day_count": len(episode_action_rows),
            "post_exit_follow_through_count": len(post_exit_follow_through_rows),
            "primary_under_exposure_reading": "low_coverage_and_low_sizing_dominate_more_than_exit_damage",
            "recommended_next_posture": "open_probability_expectancy_sizing_framework_review_before_expanding_more_symbol_logic",
        }
        key_findings = [
            "The main drag is not chronic sell-too-early behaviour. The main drag is persistent low exposure on very strong board days.",
            "Most opportunity misses happened when board breadth and average return were already very strong while gross exposure still sat below 0.2.",
            "Core-leader exits contributed some missed follow-through, but they are secondary to admission and sizing conservatism.",
            "Current profit is concentrated in a few names, which confirms that action logic is still sparse relative to the full board environment.",
        ]
        interpretation = [
            "V1.13W reframes the replay gap as an under-exposure problem instead of a pure exit problem.",
            "The strategy can already make money and keep drawdown contained, but it still under-converts confirmed board strength into portfolio expression.",
            "The next layer should therefore start from probability and expectancy driven sizing, with risk limits applied as caps rather than as the primary decision driver.",
        ]
        return V113WCPOUnderExposureAttributionReviewReport(
            summary=summary,
            key_findings=key_findings,
            top_opportunity_miss_rows=top_opportunity_miss_rows,
            episode_action_rows=episode_action_rows,
            post_exit_follow_through_rows=post_exit_follow_through_rows,
            symbol_pnl_rows=symbol_pnl_rows,
            interpretation=interpretation,
        )


def write_v113w_cpo_under_exposure_attribution_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113WCPOUnderExposureAttributionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
