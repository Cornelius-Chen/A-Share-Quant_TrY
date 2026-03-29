from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CycleMechanismReport:
    summary: dict[str, Any]
    mechanism_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mechanism_rows": self.mechanism_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CycleMechanismAnalyzer:
    """Classify incumbent-only cycle deltas into reusable drawdown mechanisms."""

    def analyze(
        self,
        *,
        bridge_payload: dict[str, Any],
        timeline_payload: dict[str, Any],
        strategy_name: str,
        incumbent_name: str,
        challenger_name: str,
    ) -> CycleMechanismReport:
        record_map = {
            (str(record["strategy_name"]), str(record["candidate_name"])): record
            for record in timeline_payload.get("candidate_records", [])
        }
        incumbent_record = record_map.get((strategy_name, incumbent_name))
        challenger_record = record_map.get((strategy_name, challenger_name))
        if incumbent_record is None or challenger_record is None:
            raise ValueError("Timeline report missing incumbent or challenger candidate record.")

        incumbent_daily = {
            str(item["trade_date"]): item for item in incumbent_record.get("daily_records", [])
        }
        challenger_daily = {
            str(item["trade_date"]): item for item in challenger_record.get("daily_records", [])
        }

        mechanism_rows = [
            self._classify_bridge_row(
                row=row,
                incumbent_daily=incumbent_daily,
                challenger_daily=challenger_daily,
            )
            for row in bridge_payload.get("bridged_cycles", [])
        ]

        avoided_negative = sum(
            1
            for row in mechanism_rows
            if row["cycle_sign"] == "negative"
            and row["mechanism_type"] == "entry_suppression_avoidance"
        )
        reduced_negative = sum(
            1
            for row in mechanism_rows
            if row["cycle_sign"] == "negative"
            and row["mechanism_type"] in {
                "earlier_exit_loss_reduction",
                "preemptive_loss_avoidance_shift",
                "carry_in_basis_advantage",
                "delayed_entry_basis_advantage",
            }
        )
        worsened_negative = sum(
            1
            for row in mechanism_rows
            if row["cycle_sign"] == "negative"
            and row["mechanism_type"] == "later_exit_loss_extension"
        )
        summary = {
            "strategy_name": strategy_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "cycle_count": len(mechanism_rows),
            "avoided_negative_cycle_count": avoided_negative,
            "reduced_negative_cycle_count": reduced_negative,
            "worsened_negative_cycle_count": worsened_negative,
            "primary_takeaway": (
                "Drawdown-specialist behavior should be read through cycle mechanisms: "
                "entry suppression, earlier loss exit, or worse delayed exit."
            ),
        }
        interpretation = [
            "Entry-suppression avoidance means the challenger never opened the incumbent's bad cycle.",
            "Earlier-exit loss reduction means both sides opened the cycle, but the challenger cut risk sooner.",
            "Carry-in basis advantage means the challenger entered before the incumbent and exited on the same day with a better basis.",
            "Delayed-entry basis advantage means the challenger entered after the incumbent and exited on the same day with a lower cost basis.",
            "Later-exit loss extension is the failure case: the challenger held the same bad cycle longer and paid for it.",
        ]
        return CycleMechanismReport(
            summary=summary,
            mechanism_rows=mechanism_rows,
            interpretation=interpretation,
        )

    def _classify_bridge_row(
        self,
        *,
        row: dict[str, Any],
        incumbent_daily: dict[str, dict[str, Any]],
        challenger_daily: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        incumbent_cycle = dict(row["incumbent_cycle"])
        inc_entry = date.fromisoformat(str(incumbent_cycle["entry_date"]))
        inc_exit = date.fromisoformat(str(incumbent_cycle["exit_date"]))
        inc_pnl = float(incumbent_cycle["pnl"])

        mechanism_type = "other_cycle_shift"
        trigger_date = None
        trigger_reason = None
        closest = row.get("closest_challenger_cycle")

        if closest is None:
            trigger_date, trigger_reason = self._find_pre_entry_buy_suppression(
                incumbent_daily=incumbent_daily,
                challenger_daily=challenger_daily,
                incumbent_entry=inc_entry,
            )
            mechanism_type = (
                "entry_suppression_avoidance"
                if inc_pnl < 0
                else "entry_suppression_opportunity_cost"
            )
        else:
            cha_entry = date.fromisoformat(str(closest["entry_date"]))
            cha_exit = date.fromisoformat(str(closest["exit_date"]))
            cha_pnl = float(closest["pnl"])
            if cha_entry == inc_entry and cha_exit < inc_exit and cha_pnl > inc_pnl:
                trigger_date, trigger_reason = self._find_exit_divergence(
                    incumbent_daily=incumbent_daily,
                    challenger_daily=challenger_daily,
                    start_date=inc_entry,
                    end_date=inc_exit,
                    mode="earlier_exit",
                )
                mechanism_type = "earlier_exit_loss_reduction"
            elif cha_entry < inc_entry and cha_exit == inc_exit and cha_pnl > inc_pnl:
                mechanism_type = "carry_in_basis_advantage"
                trigger_date = cha_entry.isoformat()
                trigger_reason = "challenger_entered_earlier_and_exited_with_better_cost_basis"
            elif cha_entry > inc_entry and cha_exit == inc_exit and cha_pnl > inc_pnl:
                mechanism_type = "delayed_entry_basis_advantage"
                trigger_date = cha_entry.isoformat()
                trigger_reason = "challenger_entered_later_and_exited_with_lower_cost_basis"
            elif cha_exit < inc_entry and cha_pnl > inc_pnl:
                mechanism_type = "preemptive_loss_avoidance_shift"
                trigger_date = cha_entry.isoformat()
                trigger_reason = "challenger_realized_smaller_loss_before_incumbent_cycle_opened"
            elif cha_entry == inc_entry and cha_exit > inc_exit and cha_pnl < inc_pnl:
                trigger_date, trigger_reason = self._find_exit_divergence(
                    incumbent_daily=incumbent_daily,
                    challenger_daily=challenger_daily,
                    start_date=inc_entry,
                    end_date=cha_exit,
                    mode="later_exit",
                )
                mechanism_type = "later_exit_loss_extension"
            elif cha_pnl > inc_pnl:
                mechanism_type = "other_reduced_loss_shift"
            else:
                mechanism_type = "other_worse_loss_shift"

        return {
            "mechanism_type": mechanism_type,
            "cycle_sign": "negative" if inc_pnl < 0 else "positive",
            "incumbent_cycle": incumbent_cycle,
            "bridge_classification": row.get("classification"),
            "closest_challenger_cycle": closest,
            "pnl_delta_vs_closest": row.get("pnl_delta_vs_closest"),
            "trigger_date": trigger_date,
            "trigger_reason": trigger_reason,
        }

    def _find_pre_entry_buy_suppression(
        self,
        *,
        incumbent_daily: dict[str, dict[str, Any]],
        challenger_daily: dict[str, dict[str, Any]],
        incumbent_entry: date,
    ) -> tuple[str | None, str | None]:
        for offset in (1, 0):
            current = (incumbent_entry - timedelta(days=offset)).isoformat()
            inc = incumbent_daily.get(current)
            cha = challenger_daily.get(current)
            if inc is None or cha is None:
                continue
            inc_actions = list(inc.get("emitted_actions", []))
            cha_actions = list(cha.get("emitted_actions", []))
            if "buy" in inc_actions and "buy" not in cha_actions:
                return current, "incumbent_opened_cycle_but_challenger_suppressed_entry"
        return None, None

    def _find_exit_divergence(
        self,
        *,
        incumbent_daily: dict[str, dict[str, Any]],
        challenger_daily: dict[str, dict[str, Any]],
        start_date: date,
        end_date: date,
        mode: str,
    ) -> tuple[str | None, str | None]:
        current = start_date
        while current <= end_date:
            day = current.isoformat()
            inc = incumbent_daily.get(day)
            cha = challenger_daily.get(day)
            if inc is None or cha is None:
                current += timedelta(days=1)
                continue
            inc_actions = list(inc.get("emitted_actions", []))
            cha_actions = list(cha.get("emitted_actions", []))
            if mode == "earlier_exit" and "sell" in cha_actions and "sell" not in inc_actions:
                return day, "challenger_exited_before_incumbent"
            if mode == "later_exit" and "sell" in inc_actions and "sell" not in cha_actions:
                return day, "incumbent_exited_before_challenger"
            current += timedelta(days=1)
        return None, None


def write_cycle_mechanism_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CycleMechanismReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
