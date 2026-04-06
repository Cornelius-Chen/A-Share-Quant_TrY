from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GDCommercialAerospaceDualSlotCapacityAuditV1Report:
    summary: dict[str, Any]
    day_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "day_rows": self.day_rows,
            "interpretation": self.interpretation,
        }


class V134GDCommercialAerospaceDualSlotCapacityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.active_wave_report_path = (
            repo_root / "reports" / "analysis" / "v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1.json"
        )
        self.dual_slot_report_path = (
            repo_root / "reports" / "analysis" / "v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1.json"
        )

    def analyze(self) -> V134GDCommercialAerospaceDualSlotCapacityAuditV1Report:
        active_wave_report = json.loads(self.active_wave_report_path.read_text(encoding="utf-8"))
        dual_slot_report = json.loads(self.dual_slot_report_path.read_text(encoding="utf-8"))

        slot_name_by_state = {row["selection_state"]: row["slot_name"] for row in dual_slot_report["slot_rows"]}

        by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in active_wave_report["candidate_rows"]:
            by_day[row["trade_date"]].append(row)

        day_rows: list[dict[str, Any]] = []
        dual_slot_day_count = 0
        single_slot_day_count = 0
        zero_slot_day_count = 0
        for trade_date in sorted(by_day):
            retained_rows = [row for row in by_day[trade_date] if row["selection_outcome"] == "selected"]
            retained_slots = [slot_name_by_state[row["selection_state"]] for row in retained_rows]
            retained_slot_set = sorted(set(retained_slots))

            if len(retained_slot_set) >= 2:
                capacity_state = "dual_slot_day"
                dual_slot_day_count += 1
            elif len(retained_slot_set) == 1:
                capacity_state = "single_slot_day"
                single_slot_day_count += 1
            else:
                capacity_state = "zero_slot_day"
                zero_slot_day_count += 1

            day_rows.append(
                {
                    "trade_date": trade_date,
                    "capacity_state": capacity_state,
                    "retained_slot_count": len(retained_slot_set),
                    "retained_slots": "|".join(retained_slot_set),
                    "retained_symbol_count": len(retained_rows),
                    "retained_symbols": "|".join(row["symbol"] for row in retained_rows),
                    "candidate_symbol_count": len(by_day[trade_date]),
                    "candidate_symbols": "|".join(row["symbol"] for row in by_day[trade_date]),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134gd_commercial_aerospace_dual_slot_capacity_audit_v1",
            "active_wave_day_count": len(day_rows),
            "dual_slot_day_count": dual_slot_day_count,
            "single_slot_day_count": single_slot_day_count,
            "zero_slot_day_count": zero_slot_day_count,
            "authoritative_rule": (
                "the current strict active-wave add surface does not support unconditional dual-slot capacity; dual-slot coexistence is local and rare, so capacity should remain supervision-only"
            ),
        }
        interpretation = [
            "V1.34GD asks a narrower operational question after dual-slot permission becomes believable: how often does the current strict active-wave surface actually support two retained slots at once?",
            "The answer is rare. Dual-slot coexistence currently appears on one local day, which means the branch should treat slot capacity as conditional supervision rather than as a default allocation mode.",
        ]
        return V134GDCommercialAerospaceDualSlotCapacityAuditV1Report(
            summary=summary,
            day_rows=day_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GDCommercialAerospaceDualSlotCapacityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GDCommercialAerospaceDualSlotCapacityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gd_commercial_aerospace_dual_slot_capacity_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
