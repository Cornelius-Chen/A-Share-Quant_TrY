from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MissedReentryChainReport:
    summary: dict[str, Any]
    chain_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "chain_rows": self.chain_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class MissedReentryChainAnalyzer:
    """Diagnose permission-loss to missed re-entry chains for one symbol."""

    def analyze(
        self,
        *,
        timeline_payload: dict[str, Any],
        path_payload: dict[str, Any],
        symbol: str,
        incumbent_name: str,
        challenger_name: str,
        missed_buy_date: str,
        position_gap_date: str,
    ) -> MissedReentryChainReport:
        candidate_records = timeline_payload.get("candidate_records", [])
        grouped: dict[str, dict[str, dict[str, Any]]] = {}
        for record in candidate_records:
            if str(record.get("symbol")) != symbol:
                continue
            grouped.setdefault(str(record["strategy_name"]), {})[str(record["candidate_name"])] = record

        path_rows = [
            row
            for row in path_payload.get("detailed_shifts", [])
            if str(row.get("trade_date")) in {missed_buy_date, position_gap_date}
        ]
        path_lookup = {
            (str(row["strategy_name"]), str(row["trade_date"])): row
            for row in path_rows
        }

        chain_rows: list[dict[str, Any]] = []
        total_missed_cycle_pnl = 0.0
        complete_chain_count = 0
        for strategy_name, candidates in sorted(grouped.items()):
            incumbent = candidates.get(incumbent_name)
            challenger = candidates.get(challenger_name)
            if incumbent is None or challenger is None:
                continue

            incumbent_days = {
                str(item["trade_date"]): item for item in incumbent.get("daily_records", [])
            }
            challenger_days = {
                str(item["trade_date"]): item for item in challenger.get("daily_records", [])
            }
            missed_buy_inc = incumbent_days.get(missed_buy_date)
            missed_buy_cha = challenger_days.get(missed_buy_date)
            gap_inc = incumbent_days.get(position_gap_date)
            gap_cha = challenger_days.get(position_gap_date)
            if missed_buy_inc is None or missed_buy_cha is None or gap_inc is None or gap_cha is None:
                continue

            incumbent_unique_trade = self._find_unique_trade(
                reference_trades=list(incumbent.get("closed_trades", [])),
                other_trades=list(challenger.get("closed_trades", [])),
                entry_date=position_gap_date,
            )
            challenger_unique_trade = self._find_unique_trade(
                reference_trades=list(challenger.get("closed_trades", [])),
                other_trades=list(incumbent.get("closed_trades", [])),
                entry_date=missed_buy_date,
            )
            incumbent_unique_pnl = (
                round(float(incumbent_unique_trade["pnl"]), 6)
                if incumbent_unique_trade is not None
                else 0.0
            )
            challenger_unique_pnl = (
                round(float(challenger_unique_trade["pnl"]), 6)
                if challenger_unique_trade is not None
                else 0.0
            )
            net_chain_pnl_delta = round(challenger_unique_pnl - incumbent_unique_pnl, 6)
            total_missed_cycle_pnl += incumbent_unique_pnl

            missed_buy_triggered = (
                bool(missed_buy_inc.get("permission_allowed"))
                and not bool(missed_buy_cha.get("permission_allowed"))
                and "buy" in list(missed_buy_inc.get("emitted_actions", []))
                and "buy" not in list(missed_buy_cha.get("emitted_actions", []))
            )
            position_gap_triggered = (
                int(gap_inc.get("position_qty", 0)) > int(gap_cha.get("position_qty", 0))
                and "sell" in list(gap_inc.get("emitted_actions", []))
                and "sell" not in list(gap_cha.get("emitted_actions", []))
            )
            complete_chain = missed_buy_triggered and position_gap_triggered
            if complete_chain:
                complete_chain_count += 1

            chain_rows.append(
                {
                    "strategy_name": strategy_name,
                    "missed_buy_date": missed_buy_date,
                    "position_gap_date": position_gap_date,
                    "missed_buy_triggered": missed_buy_triggered,
                    "position_gap_triggered": position_gap_triggered,
                    "complete_chain": complete_chain,
                    "missed_buy_split": {
                        "incumbent_permission_allowed": missed_buy_inc["permission_allowed"],
                        "challenger_permission_allowed": missed_buy_cha["permission_allowed"],
                        "incumbent_approved_sector_id": missed_buy_inc["approved_sector_id"],
                        "challenger_approved_sector_id": missed_buy_cha["approved_sector_id"],
                        "incumbent_emitted_actions": missed_buy_inc["emitted_actions"],
                        "challenger_emitted_actions": missed_buy_cha["emitted_actions"],
                    },
                    "position_gap_split": {
                        "incumbent_position_qty": gap_inc["position_qty"],
                        "challenger_position_qty": gap_cha["position_qty"],
                        "incumbent_emitted_actions": gap_inc["emitted_actions"],
                        "challenger_emitted_actions": gap_cha["emitted_actions"],
                        "incumbent_exit_reason": gap_inc["exit_reason"],
                        "challenger_exit_reason": gap_cha["exit_reason"],
                    },
                    "path_rows": {
                        "missed_buy_path": path_lookup.get((strategy_name, missed_buy_date)),
                        "position_gap_path": path_lookup.get((strategy_name, position_gap_date)),
                    },
                    "incumbent_unique_trade": incumbent_unique_trade,
                    "challenger_unique_trade": challenger_unique_trade,
                    "incumbent_unique_trade_pnl": incumbent_unique_pnl,
                    "challenger_unique_trade_pnl": challenger_unique_pnl,
                    "net_chain_pnl_delta": net_chain_pnl_delta,
                }
            )

        summary = {
            "symbol": symbol,
            "strategy_count": len(chain_rows),
            "missed_buy_date": missed_buy_date,
            "position_gap_date": position_gap_date,
            "complete_chain_count": complete_chain_count,
            "complete_chain_ratio": round(
                complete_chain_count / len(chain_rows), 6
            ) if chain_rows else 0.0,
            "incumbent_missed_cycle_total_pnl": round(total_missed_cycle_pnl, 6),
            "mean_incumbent_missed_cycle_pnl": round(
                total_missed_cycle_pnl / len(chain_rows), 6
            ) if chain_rows else 0.0,
            "dominant_rule": (
                "Permission-loss only matters when it suppresses a buy and propagates "
                "into a later position-gap exit on the incumbent side."
            ),
        }
        interpretation = [
            "The dominant chain is not just a threshold-edge permission split; it is the combination of a missed buy and the later absence of a position that the incumbent still exits.",
            "If the challenger loses permission on the re-entry day but the later position state stays matched, the split remains mostly latent.",
            "The highest-value repair target is therefore the date pair where permission loss directly removes the incumbent-only re-entry cycle.",
        ]
        return MissedReentryChainReport(
            summary=summary,
            chain_rows=chain_rows,
            interpretation=interpretation,
        )

    def _find_unique_trade(
        self,
        *,
        reference_trades: list[dict[str, Any]],
        other_trades: list[dict[str, Any]],
        entry_date: str,
    ) -> dict[str, Any] | None:
        other_signatures = {self._trade_signature(item) for item in other_trades}
        for trade in reference_trades:
            if str(trade.get("entry_date")) != entry_date:
                continue
            if self._trade_signature(trade) in other_signatures:
                continue
            return trade
        return None

    def _trade_signature(self, trade: dict[str, Any]) -> tuple[Any, ...]:
        return (
            str(trade.get("entry_date")),
            str(trade.get("exit_date")),
            int(trade.get("quantity", 0)),
            round(float(trade.get("entry_price", 0.0)), 6),
            round(float(trade.get("exit_price", 0.0)), 6),
        )


def write_missed_reentry_chain_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MissedReentryChainReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
