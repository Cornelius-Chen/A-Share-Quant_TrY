from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SymbolPathShiftReport:
    source_report: str
    summary: dict[str, Any]
    strategy_shift_summary: list[dict[str, Any]]
    repeated_shift_dates: list[dict[str, Any]]
    detailed_shifts: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_report": self.source_report,
            "summary": self.summary,
            "strategy_shift_summary": self.strategy_shift_summary,
            "repeated_shift_dates": self.repeated_shift_dates,
            "detailed_shifts": self.detailed_shifts,
        }


def load_timeline_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Timeline report at {path} must decode to a mapping.")
    return payload


class SymbolPathShiftAnalyzer:
    """Explain daily path shifts between incumbent and challenger for one symbol."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        incumbent_name: str,
        challenger_name: str,
    ) -> SymbolPathShiftReport:
        candidate_records = payload.get("candidate_records", [])
        if not isinstance(candidate_records, list):
            raise ValueError("Timeline report must contain candidate_records.")

        grouped: dict[str, dict[str, dict[str, Any]]] = {}
        for record in candidate_records:
            grouped.setdefault(str(record["strategy_name"]), {})[str(record["candidate_name"])] = record

        strategy_shift_summary: list[dict[str, Any]] = []
        detailed_shifts: list[dict[str, Any]] = []
        date_counter: dict[str, int] = {}
        for strategy_name, candidates in sorted(grouped.items()):
            incumbent = candidates.get(incumbent_name)
            challenger = candidates.get(challenger_name)
            if incumbent is None or challenger is None:
                continue
            strategy_shifts = self._compare_strategy(
                strategy_name=strategy_name,
                incumbent=incumbent,
                challenger=challenger,
            )
            detailed_shifts.extend(strategy_shifts)
            for shift in strategy_shifts:
                date_counter[str(shift["trade_date"])] = date_counter.get(str(shift["trade_date"]), 0) + 1
            strategy_shift_summary.append(
                {
                    "strategy_name": strategy_name,
                    "shift_count": len(strategy_shifts),
                    "first_shift_date": strategy_shifts[0]["trade_date"] if strategy_shifts else None,
                    "largest_shift": strategy_shifts[0] if strategy_shifts else None,
                }
            )

        repeated_shift_dates = sorted(
            (
                {"trade_date": trade_date, "strategy_count": count}
                for trade_date, count in date_counter.items()
                if count > 1
            ),
            key=lambda item: (-int(item["strategy_count"]), str(item["trade_date"])),
        )
        summary = {
            "strategy_count": len(strategy_shift_summary),
            "shift_row_count": len(detailed_shifts),
            "most_repeated_shift_date": repeated_shift_dates[0] if repeated_shift_dates else None,
            "interpretation": [
                "Repeated shift dates across strategies are the strongest evidence of a real path-sequence difference.",
                "Approval-sector and emitted-action changes are usually more actionable than passive score differences.",
                "A symbol-level replay becomes promotion-relevant only when the same shift pattern repeats across multiple strategies.",
            ],
        }
        return SymbolPathShiftReport(
            source_report=str(payload.get("summary", {}).get("symbol", "symbol_timeline_replay")),
            summary=summary,
            strategy_shift_summary=strategy_shift_summary,
            repeated_shift_dates=repeated_shift_dates,
            detailed_shifts=detailed_shifts[:24],
        )

    def _compare_strategy(
        self,
        *,
        strategy_name: str,
        incumbent: dict[str, Any],
        challenger: dict[str, Any],
    ) -> list[dict[str, Any]]:
        incumbent_days = {str(item["trade_date"]): item for item in incumbent.get("daily_records", [])}
        challenger_days = {str(item["trade_date"]): item for item in challenger.get("daily_records", [])}
        shifts: list[dict[str, Any]] = []
        for trade_date in sorted(set(incumbent_days) | set(challenger_days)):
            inc = incumbent_days.get(trade_date)
            cha = challenger_days.get(trade_date)
            if inc is None or cha is None:
                continue
            differences: list[str] = []
            if bool(inc["permission_allowed"]) != bool(cha["permission_allowed"]):
                differences.append("permission")
            if str(inc["approved_sector_id"]) != str(cha["approved_sector_id"]):
                differences.append("approved_sector")
            if str(inc["assignment_layer"]) != str(cha["assignment_layer"]):
                differences.append("assignment_layer")
            if str(inc["assignment_reason"]) != str(cha["assignment_reason"]):
                differences.append("assignment_reason")
            if list(inc["emitted_actions"]) != list(cha["emitted_actions"]):
                differences.append("emitted_actions")
            if bool(inc["pending_buy"]) != bool(cha["pending_buy"]):
                differences.append("pending_buy")
            if bool(inc["pending_sell"]) != bool(cha["pending_sell"]):
                differences.append("pending_sell")
            if int(inc["position_qty"]) != int(cha["position_qty"]):
                differences.append("position_qty")
            if str(inc["exit_reason"]) != str(cha["exit_reason"]):
                differences.append("exit_reason")
            if not differences:
                continue
            shifts.append(
                {
                    "strategy_name": strategy_name,
                    "trade_date": trade_date,
                    "difference_types": differences,
                    "incumbent_permission_allowed": inc["permission_allowed"],
                    "challenger_permission_allowed": cha["permission_allowed"],
                    "incumbent_approved_sector_id": inc["approved_sector_id"],
                    "challenger_approved_sector_id": cha["approved_sector_id"],
                    "incumbent_assignment_layer": inc["assignment_layer"],
                    "challenger_assignment_layer": cha["assignment_layer"],
                    "incumbent_assignment_reason": inc["assignment_reason"],
                    "challenger_assignment_reason": cha["assignment_reason"],
                    "incumbent_emitted_actions": inc["emitted_actions"],
                    "challenger_emitted_actions": cha["emitted_actions"],
                    "incumbent_position_qty": inc["position_qty"],
                    "challenger_position_qty": cha["position_qty"],
                    "incumbent_exit_reason": inc["exit_reason"],
                    "challenger_exit_reason": cha["exit_reason"],
                }
            )
        return shifts


def write_symbol_path_shift_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SymbolPathShiftReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
