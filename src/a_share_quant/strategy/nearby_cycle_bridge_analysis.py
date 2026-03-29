from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class NearbyCycleBridgeReport:
    summary: dict[str, Any]
    bridged_cycles: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bridged_cycles": self.bridged_cycles,
            "interpretation": self.interpretation,
        }


def load_cycle_delta_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Cycle delta report at {path} must decode to a mapping.")
    return payload


def load_timeline_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Timeline report at {path} must decode to a mapping.")
    return payload


class NearbyCycleBridgeAnalyzer:
    """Relate incumbent-only cycles to nearby challenger cycles."""

    def analyze(
        self,
        *,
        cycle_delta_payload: dict[str, Any],
        timeline_payload: dict[str, Any],
        strategy_name: str,
        incumbent_name: str,
        challenger_name: str,
        bridge_days: int = 1,
    ) -> NearbyCycleBridgeReport:
        candidate_records = timeline_payload.get("candidate_records", [])
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

        challenger_cycles = list(challenger.get("closed_trades", []))
        incumbent_only_cycles = list(cycle_delta_payload.get("incumbent_only_cycles", []))
        bridged_cycles: list[dict[str, Any]] = []
        for cycle in incumbent_only_cycles:
            bridge = self._bridge_cycle(cycle=cycle, challenger_cycles=challenger_cycles, bridge_days=bridge_days)
            bridged_cycles.append(bridge)

        summary = {
            "strategy_name": strategy_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "bridge_days": bridge_days,
            "incumbent_only_cycle_count": len(incumbent_only_cycles),
            "avoided_cycle_count": sum(1 for item in bridged_cycles if item["classification"] == "avoided_cycle"),
            "reduced_loss_cycle_count": sum(1 for item in bridged_cycles if item["classification"] == "reduced_loss_nearby_cycle"),
            "worse_loss_cycle_count": sum(1 for item in bridged_cycles if item["classification"] == "worse_nearby_cycle"),
        }
        interpretation = [
            "A drawdown-specialist branch is strongest when it either avoids a bad incumbent-only cycle entirely or converts it into a nearby smaller loss.",
            "A nearby challenger cycle is still useful if it shrinks loss enough; full avoidance is not the only valid drawdown mechanism.",
            "Worse nearby cycles matter because they show where the specialist pays for its stricter posture.",
        ]
        return NearbyCycleBridgeReport(
            summary=summary,
            bridged_cycles=bridged_cycles,
            interpretation=interpretation,
        )

    def _bridge_cycle(
        self,
        *,
        cycle: dict[str, Any],
        challenger_cycles: list[dict[str, Any]],
        bridge_days: int,
    ) -> dict[str, Any]:
        inc_entry = date.fromisoformat(str(cycle["entry_date"]))
        inc_exit = date.fromisoformat(str(cycle["exit_date"]))
        lower = inc_entry - timedelta(days=bridge_days)
        upper = inc_exit + timedelta(days=bridge_days)

        nearby = []
        for challenger_cycle in challenger_cycles:
            cha_entry = date.fromisoformat(str(challenger_cycle["entry_date"]))
            cha_exit = date.fromisoformat(str(challenger_cycle["exit_date"]))
            if cha_exit < lower or cha_entry > upper:
                continue
            nearby.append(challenger_cycle)

        result = {
            "incumbent_cycle": cycle,
            "classification": "avoided_cycle" if not nearby else "nearby_cycle_found",
            "challenger_cycles": nearby,
        }
        if not nearby:
            return result

        closest = min(
            nearby,
            key=lambda item: (
                abs((date.fromisoformat(str(item["entry_date"])) - inc_entry).days),
                abs((date.fromisoformat(str(item["exit_date"])) - inc_exit).days),
            ),
        )
        inc_pnl = float(cycle["pnl"])
        cha_pnl = float(closest["pnl"])
        if cha_pnl > inc_pnl:
            classification = "reduced_loss_nearby_cycle"
        elif cha_pnl < inc_pnl:
            classification = "worse_nearby_cycle"
        else:
            classification = "same_loss_nearby_cycle"

        result.update(
            {
                "classification": classification,
                "closest_challenger_cycle": closest,
                "pnl_delta_vs_closest": round(cha_pnl - inc_pnl, 6),
            }
        )
        return result


def write_nearby_cycle_bridge_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: NearbyCycleBridgeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
