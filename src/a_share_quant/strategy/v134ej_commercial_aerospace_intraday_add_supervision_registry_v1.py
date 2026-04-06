from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOCKOUT_START_DATE = 20260115
FAILED_ADD_CASES = {
    ("20260113", "000738"),
    ("20260113", "601698"),
}


@dataclass(slots=True)
class V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Report:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.orders_path = repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"

    @staticmethod
    def _family_from_reason(reason: str) -> str:
        if reason == "phase_geometry_preheat_probe":
            return "preheat_probe_add"
        if reason == "phase_geometry_preheat_full":
            return "preheat_full_add"
        if reason == "phase_geometry_impulse_full":
            return "impulse_full_add"
        return "unknown_add_family"

    def analyze(self) -> V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Report:
        registry_rows: list[dict[str, Any]] = []
        with self.orders_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["action"] not in {"open", "add"}:
                    continue
                execution_trade_date = row["execution_trade_date"]
                symbol = row["symbol"]
                date_int = int(execution_trade_date)
                board_lockout_active = date_int >= LOCKOUT_START_DATE
                local_only_rebound_guard = execution_trade_date == "20260126"
                is_failed_add = (execution_trade_date, symbol) in FAILED_ADD_CASES

                if board_lockout_active:
                    supervision_tier = "blocked_add_seed"
                    supervision_detail = "board_lockout_active"
                elif is_failed_add:
                    supervision_tier = "failed_add_seed"
                    supervision_detail = "same_day_intraday_failure_after_add"
                else:
                    supervision_tier = "allowed_add_seed"
                    supervision_detail = "pre_lockout_add_path"

                registry_rows.append(
                    {
                        "execution_trade_date": execution_trade_date,
                        "signal_trade_date": row["signal_trade_date"],
                        "symbol": symbol,
                        "action": row["action"],
                        "reason": row["reason"],
                        "seed_family": self._family_from_reason(row["reason"]),
                        "supervision_tier": supervision_tier,
                        "supervision_detail": supervision_detail,
                        "board_lockout_active": board_lockout_active,
                        "local_only_rebound_guard": local_only_rebound_guard,
                        "weight_vs_initial_capital": row["weight_vs_initial_capital"],
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(registry_rows)

        allowed_count = sum(1 for row in registry_rows if row["supervision_tier"] == "allowed_add_seed")
        failed_count = sum(1 for row in registry_rows if row["supervision_tier"] == "failed_add_seed")
        blocked_count = sum(1 for row in registry_rows if row["supervision_tier"] == "blocked_add_seed")
        summary = {
            "acceptance_posture": "build_v134ej_commercial_aerospace_intraday_add_supervision_registry_v1",
            "registry_row_count": len(registry_rows),
            "allowed_add_seed_count": allowed_count,
            "failed_add_seed_count": failed_count,
            "blocked_add_seed_count": blocked_count,
            "seed_family_count": len({row["seed_family"] for row in registry_rows}),
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_supervision_registry_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34EJ bootstraps the first intraday-add supervision registry from the existing open/add execution surface.",
            "The registry stays deliberately coarse: allowed, failed, and blocked add seeds are enough to start the frontier without pretending add execution already exists.",
        ]
        return V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Report(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ej_commercial_aerospace_intraday_add_supervision_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
