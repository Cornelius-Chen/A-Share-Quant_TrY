from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SymbolCycleDeltaReport:
    summary: dict[str, Any]
    incumbent_only_cycles: list[dict[str, Any]]
    challenger_only_cycles: list[dict[str, Any]]
    matched_cycles: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "incumbent_only_cycles": self.incumbent_only_cycles,
            "challenger_only_cycles": self.challenger_only_cycles,
            "matched_cycles": self.matched_cycles,
            "interpretation": self.interpretation,
        }


def load_timeline_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Timeline report at {path} must decode to a mapping.")
    return payload


class SymbolCycleDeltaAnalyzer:
    """Compare exact closed-trade cycles between incumbent and challenger."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        strategy_name: str,
        incumbent_name: str,
        challenger_name: str,
    ) -> SymbolCycleDeltaReport:
        candidate_records = payload.get("candidate_records", [])
        if not isinstance(candidate_records, list):
            raise ValueError("Timeline report must contain candidate_records.")

        record_map = {
            str(record["candidate_name"]): record
            for record in candidate_records
            if str(record["strategy_name"]) == strategy_name
        }
        incumbent = record_map.get(incumbent_name)
        challenger = record_map.get(challenger_name)
        if incumbent is None or challenger is None:
            raise ValueError("Incumbent or challenger record missing for requested strategy.")

        incumbent_cycles = {
            (str(item["entry_date"]), str(item["exit_date"])): item
            for item in incumbent.get("closed_trades", [])
        }
        challenger_cycles = {
            (str(item["entry_date"]), str(item["exit_date"])): item
            for item in challenger.get("closed_trades", [])
        }

        incumbent_only = [
            incumbent_cycles[key]
            for key in incumbent_cycles.keys() - challenger_cycles.keys()
        ]
        challenger_only = [
            challenger_cycles[key]
            for key in challenger_cycles.keys() - incumbent_cycles.keys()
        ]
        matched = []
        for key in incumbent_cycles.keys() & challenger_cycles.keys():
            inc = incumbent_cycles[key]
            cha = challenger_cycles[key]
            matched.append(
                {
                    "entry_date": key[0],
                    "exit_date": key[1],
                    "incumbent_pnl": inc["pnl"],
                    "challenger_pnl": cha["pnl"],
                    "pnl_delta": round(float(cha["pnl"]) - float(inc["pnl"]), 6),
                    "holding_day_delta": int(cha["holding_days"]) - int(inc["holding_days"]),
                }
            )

        incumbent_only.sort(key=lambda item: float(item["pnl"]))
        challenger_only.sort(key=lambda item: float(item["pnl"]))
        matched.sort(key=lambda item: float(item["pnl_delta"]))

        summary = {
            "strategy_name": strategy_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "incumbent_only_cycle_count": len(incumbent_only),
            "challenger_only_cycle_count": len(challenger_only),
            "matched_cycle_count": len(matched),
            "incumbent_only_total_pnl": round(sum(float(item["pnl"]) for item in incumbent_only), 6),
            "challenger_only_total_pnl": round(sum(float(item["pnl"]) for item in challenger_only), 6),
        }
        interpretation = [
            "Incumbent-only negative cycles are the cleanest evidence that a specialist branch reduced churn or filtered low-quality re-entries.",
            "Challenger-only cycles matter too, but for drawdown pockets the first question is usually which bad cycles disappeared.",
            "Exact-cycle matching is intentionally strict; unmatched but nearby cycles should be replayed separately if they still matter.",
        ]
        return SymbolCycleDeltaReport(
            summary=summary,
            incumbent_only_cycles=incumbent_only,
            challenger_only_cycles=challenger_only,
            matched_cycles=matched,
            interpretation=interpretation,
        )


def write_symbol_cycle_delta_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SymbolCycleDeltaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
