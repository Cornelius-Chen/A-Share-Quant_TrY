from __future__ import annotations

import csv
import json
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132c_commercial_aerospace_local_1min_seed_window_extraction_v1 import (
    _symbol_to_archive_member,
)
from a_share_quant.strategy.v134c_commercial_aerospace_intraday_seed_simulator_v1 import _calc_costs


@dataclass(slots=True)
class V134ECommercialAerospaceIntradaySeedSimulatorAttributionReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "symbol_rows": self.symbol_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134ECommercialAerospaceIntradaySeedSimulatorAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sim_report_path = (
            repo_root / "reports" / "analysis" / "v134c_commercial_aerospace_intraday_seed_simulator_v1.json"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_seed_simulator_attribution_v1.csv"
        )

    def _session_close_price(self, trade_date: str, symbol: str) -> float:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        return float(rows[-1][4])

    def analyze(self) -> V134ECommercialAerospaceIntradaySeedSimulatorAttributionReport:
        sim = json.loads(self.sim_report_path.read_text(encoding="utf-8"))
        order_rows = sim["order_rows"]
        sim_session_rows = sim["session_rows"]

        close_cache: dict[tuple[str, str], float] = {}
        enriched_rows: list[dict[str, Any]] = []
        for row in order_rows:
            session_key = (row["execution_trade_date"], row["symbol"])
            session_close = close_cache.setdefault(
                session_key,
                self._session_close_price(*session_key),
            )
            sell_quantity = float(row["sell_quantity"])
            close_notional = sell_quantity * session_close
            close_costs = _calc_costs(close_notional, action="sell")
            close_pnl_before_cost = sell_quantity * (session_close - float(row["entry_price"]))
            close_pnl_after_cost = close_pnl_before_cost - close_costs["total_cost"]
            same_day_loss_avoided = float(row["pnl_after_cost"]) - close_pnl_after_cost
            enriched = dict(row)
            enriched["session_close_price"] = round(session_close, 4)
            enriched["close_exit_pnl_after_cost"] = round(close_pnl_after_cost, 4)
            enriched["same_day_loss_avoided"] = round(same_day_loss_avoided, 4)
            enriched_rows.append(enriched)

        tier_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        symbol_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        session_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in enriched_rows:
            tier_groups[row["trigger_tier"]].append(row)
            symbol_groups[row["symbol"]].append(row)
            session_groups[(row["execution_trade_date"], row["symbol"])].append(row)

        total_loss_avoided = sum(float(row["same_day_loss_avoided"]) for row in enriched_rows)

        tier_rows = []
        for tier, rows in sorted(tier_groups.items()):
            same_day_avoided = sum(float(row["same_day_loss_avoided"]) for row in rows)
            tier_rows.append(
                {
                    "trigger_tier": tier,
                    "order_count": len(rows),
                    "sell_notional": round(sum(float(row["sell_notional"]) for row in rows), 4),
                    "pnl_after_cost": round(sum(float(row["pnl_after_cost"]) for row in rows), 4),
                    "same_day_loss_avoided": round(same_day_avoided, 4),
                    "same_day_loss_avoided_share": round(same_day_avoided / total_loss_avoided, 6)
                    if total_loss_avoided
                    else 0.0,
                }
            )

        symbol_rows = []
        for symbol, rows in sorted(symbol_groups.items()):
            same_day_avoided = sum(float(row["same_day_loss_avoided"]) for row in rows)
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "order_count": len(rows),
                    "pnl_after_cost": round(sum(float(row["pnl_after_cost"]) for row in rows), 4),
                    "same_day_loss_avoided": round(same_day_avoided, 4),
                    "same_day_loss_avoided_share": round(same_day_avoided / total_loss_avoided, 6)
                    if total_loss_avoided
                    else 0.0,
                }
            )

        session_lookup = {
            (row["execution_trade_date"], row["symbol"]): row for row in sim_session_rows
        }
        session_rows = []
        for session_key, rows in sorted(session_groups.items()):
            trade_date, symbol = session_key
            same_day_avoided = sum(float(row["same_day_loss_avoided"]) for row in rows)
            session_meta = session_lookup[session_key]
            session_rows.append(
                {
                    "execution_trade_date": trade_date,
                    "symbol": symbol,
                    "phase_window_semantic": session_meta["phase_window_semantic"],
                    "severity_tier": session_meta["severity_tier"],
                    "filled_step_count": session_meta["filled_step_count"],
                    "remaining_quantity_after_sim": session_meta["remaining_quantity_after_sim"],
                    "pnl_after_cost": round(sum(float(row["pnl_after_cost"]) for row in rows), 4),
                    "same_day_loss_avoided": round(same_day_avoided, 4),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        top_symbol = max(symbol_rows, key=lambda row: row["same_day_loss_avoided"])
        top_tier = max(tier_rows, key=lambda row: row["same_day_loss_avoided"])

        summary = {
            "acceptance_posture": "freeze_v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1",
            "order_count": len(enriched_rows),
            "session_count": len(session_rows),
            "same_day_loss_avoided_total": round(total_loss_avoided, 4),
            "top_symbol_by_same_day_loss_avoided": top_symbol["symbol"],
            "top_tier_by_same_day_loss_avoided": top_tier["trigger_tier"],
            "attribution_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_seed_simulator_attribution_ready_for_phase_2_direction_triage",
        }
        interpretation = [
            "V1.34E explains which seed sessions, tiers, and symbols drive the first intraday seed simulator's shadow-risk benefit.",
            "The report is still phase-2-only: it attributes same-day damage avoidance inside the canonical seed set without opening replay binding.",
        ]
        return V134ECommercialAerospaceIntradaySeedSimulatorAttributionReport(
            summary=summary,
            tier_rows=tier_rows,
            symbol_rows=symbol_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ECommercialAerospaceIntradaySeedSimulatorAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ECommercialAerospaceIntradaySeedSimulatorAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
