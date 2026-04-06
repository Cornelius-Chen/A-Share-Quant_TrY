from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LATE_PREHEAT_START = "20251212"
LATE_PREHEAT_END = "20251223"


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V129ICommercialAerospaceLatePreheatEntryMismatchAuditReport:
    summary: dict[str, Any]
    mismatch_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mismatch_rows": self.mismatch_rows,
            "interpretation": self.interpretation,
        }


class V129ICommercialAerospaceLatePreheatEntryMismatchAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.orders_path = repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        self.state_table_path = repo_root / "data" / "training" / "commercial_aerospace_state_machine_supervised_table_v1.csv"

    @staticmethod
    def _previous_trade_date(rows: list[dict[str, str]], execution_trade_date: str) -> str:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        idx = ordered_dates.index(execution_trade_date)
        return ordered_dates[idx - 1]

    def analyze(self) -> V129ICommercialAerospaceLatePreheatEntryMismatchAuditReport:
        orders = _load_csv(self.orders_path)
        state_rows = _load_csv(self.state_table_path)
        state_map = {(row["trade_date"], row["symbol"]): row for row in state_rows}

        late_preheat_orders = [
            row
            for row in orders
            if row["action"] == "open"
            and LATE_PREHEAT_START <= row["execution_trade_date"] <= LATE_PREHEAT_END
            and row["reason"] == "phase_geometry_preheat_full"
        ]

        mismatch_rows: list[dict[str, Any]] = []
        for order in late_preheat_orders:
            signal_trade_date = self._previous_trade_date(state_rows, order["execution_trade_date"])
            state_row = state_map[(signal_trade_date, order["symbol"])]
            if state_row["supervised_action_state"] != "full_pre":
                mismatch_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "execution_trade_date": order["execution_trade_date"],
                        "symbol": order["symbol"],
                        "order_reason": order["reason"],
                        "state_machine_label": state_row["supervised_action_state"],
                        "forward_return_10": round(float(state_row["forward_return_10"]), 8),
                        "max_adverse_return_10": round(float(state_row["max_adverse_return_10"]), 8),
                        "event_state": state_row["event_state"],
                        "regime_proxy_semantic": state_row["regime_proxy_semantic"],
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v129i_commercial_aerospace_late_preheat_entry_mismatch_audit_v1",
            "late_preheat_full_order_count": len(late_preheat_orders),
            "late_preheat_full_mismatch_count": len(mismatch_rows),
            "late_preheat_full_mismatch_rate": round(len(mismatch_rows) / len(late_preheat_orders), 8) if late_preheat_orders else 0.0,
            "authoritative_rule": "late-preheat full entries that do not align with the phase-specific full_pre state should be treated as governance failures before any replay-side expansion is attempted",
        }
        interpretation = [
            "V1.29I audits whether the current primary replay's late-preheat full adds actually align with the newly lawful full_pre supervision layer.",
            "This is governance-only: it identifies over-escalated preheat entries without reopening replay tuning.",
        ]
        return V129ICommercialAerospaceLatePreheatEntryMismatchAuditReport(
            summary=summary,
            mismatch_rows=mismatch_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129ICommercialAerospaceLatePreheatEntryMismatchAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129ICommercialAerospaceLatePreheatEntryMismatchAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129i_commercial_aerospace_late_preheat_entry_mismatch_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
