from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Report:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_orders_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.phase2_session_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_sessions_v1.csv"
        )
        self.phase2_stack_path = (
            repo_root / "reports" / "analysis" / "v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_holdings_aware_sell_binding_audit_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Report:
        primary_orders = self._load_csv(self.primary_orders_path)
        phase2_sessions = self._load_csv(self.phase2_session_path)
        phase2_stack = json.loads(self.phase2_stack_path.read_text(encoding="utf-8"))

        orders_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in primary_orders:
            orders_by_date[row["execution_trade_date"]].append(row)

        all_dates = sorted(set(orders_by_date) | {row["trade_date"] for row in phase2_sessions})
        holdings: dict[str, int] = defaultdict(int)
        start_of_day_quantity: dict[tuple[str, str], int] = {}

        sessions_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in phase2_sessions:
            sessions_by_date[row["trade_date"]].append(row)

        for trade_date in all_dates:
            symbols = (
                set(holdings)
                | {row["symbol"] for row in orders_by_date.get(trade_date, [])}
                | {row["symbol"] for row in sessions_by_date.get(trade_date, [])}
            )
            for symbol in symbols:
                start_of_day_quantity[(trade_date, symbol)] = holdings.get(symbol, 0)
            for row in orders_by_date.get(trade_date, []):
                quantity = int(float(row["quantity"]))
                if row["action"] in {"open", "add"}:
                    holdings[row["symbol"]] += quantity
                elif row["action"] in {"reduce", "close"}:
                    holdings[row["symbol"]] -= quantity

        session_rows: list[dict[str, Any]] = []
        for row in phase2_sessions:
            trade_date = row["trade_date"]
            symbol = row["symbol"]
            reference_quantity = int(float(row["reference_quantity"]))
            start_qty = start_of_day_quantity[(trade_date, symbol)]
            same_day_primary_rows = [r for r in orders_by_date.get(trade_date, []) if r["symbol"] == symbol]

            if start_qty <= 0:
                holding_status = "no_actual_holding"
            elif start_qty >= reference_quantity:
                holding_status = "fully_funded_overlap"
            else:
                holding_status = "underfunded_vs_reference"

            session_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "predicted_tier": row["predicted_tier"],
                    "reference_quantity": reference_quantity,
                    "actual_start_of_day_quantity": start_qty,
                    "actual_vs_reference_ratio": round(start_qty / reference_quantity, 6) if reference_quantity else 0.0,
                    "holding_status": holding_status,
                    "same_day_primary_action_count": len(same_day_primary_rows),
                    "same_day_primary_actions": "|".join(sorted({r["action"] for r in same_day_primary_rows})) or "",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        summary = {
            "acceptance_posture": "freeze_v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1",
            "phase2_wider_reference": phase2_stack["summary"]["current_phase2_wider_reference"],
            "broader_hit_session_count": len(session_rows),
            "positive_start_quantity_count": sum(
                1 for row in session_rows if row["actual_start_of_day_quantity"] > 0
            ),
            "fully_funded_overlap_count": sum(
                1 for row in session_rows if row["holding_status"] == "fully_funded_overlap"
            ),
            "underfunded_overlap_count": sum(
                1 for row in session_rows if row["holding_status"] == "underfunded_vs_reference"
            ),
            "no_actual_holding_count": sum(1 for row in session_rows if row["holding_status"] == "no_actual_holding"),
            "same_day_primary_collision_count": sum(
                1 for row in session_rows if row["same_day_primary_action_count"] > 0
            ),
            "audit_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_holdings_aware_sell_binding_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BU checks whether the current phase-2 wider sell shadow can be mapped onto the frozen EOD primary's actual holdings.",
            "The audit shows that holdings-aware binding is not blocked by missing sell logic. It is blocked because the current wider shadow is mostly reference-notional and only partially overlaps real start-of-day positions.",
        ]
        return V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Report(
            summary=summary,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
