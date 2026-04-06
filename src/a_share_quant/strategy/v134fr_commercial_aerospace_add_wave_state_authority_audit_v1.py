from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Report:
    summary: dict[str, Any]
    day_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "day_rows": self.day_rows,
            "interpretation": self.interpretation,
        }


class V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.day_level_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_day_level_selection_authority_days_v1.csv"
        )
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.output_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_wave_state_authority_days_v1.csv"
        )

    def analyze(self) -> V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Report:
        with self.day_level_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            day_rows = list(csv.DictReader(handle))

        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            context_rows = list(csv.DictReader(handle))
        trading_calendar = sorted(set(row["trade_date"] for row in context_rows))
        trading_index = {trade_date: idx for idx, trade_date in enumerate(trading_calendar)}

        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            order_rows = list(csv.DictReader(handle))

        orders_by_day: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in order_rows:
            orders_by_day[row["execution_trade_date"]].append(row)

        enriched_rows: list[dict[str, Any]] = []
        for row in day_rows:
            trade_date = row["trade_date"]
            idx = trading_index[trade_date]
            prev_1d = trading_calendar[max(0, idx - 1) : idx]
            prev_2d = trading_calendar[max(0, idx - 2) : idx]

            trailing_openadd_1d = sum(
                1 for day in prev_1d for order in orders_by_day.get(day, []) if order["action"] in {"open", "add"}
            )
            trailing_reduce_1d = sum(
                1
                for day in prev_1d
                for order in orders_by_day.get(day, [])
                if order["action"] in {"reduce", "close"}
            )
            trailing_openadd_2d = sum(
                1 for day in prev_2d for order in orders_by_day.get(day, []) if order["action"] in {"open", "add"}
            )
            trailing_reduce_2d = sum(
                1
                for day in prev_2d
                for order in orders_by_day.get(day, [])
                if order["action"] in {"reduce", "close"}
            )

            if trailing_openadd_1d == 0 and trailing_reduce_1d > 0:
                wave_state = "post_wave_echo_guard"
            else:
                wave_state = "active_wave_selection_day"

            enriched_rows.append(
                {
                    **row,
                    "trailing_openadd_1d": trailing_openadd_1d,
                    "trailing_reduce_1d": trailing_reduce_1d,
                    "trailing_openadd_2d": trailing_openadd_2d,
                    "trailing_reduce_2d": trailing_reduce_2d,
                    "wave_state": wave_state,
                }
            )

        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(enriched_rows[0].keys()))
            writer.writeheader()
            writer.writerows(enriched_rows)

        active_wave_days = [row for row in enriched_rows if row["wave_state"] == "active_wave_selection_day"]
        post_wave_days = [row for row in enriched_rows if row["wave_state"] == "post_wave_echo_guard"]

        summary = {
            "acceptance_posture": "freeze_v134fr_commercial_aerospace_add_wave_state_authority_audit_v1",
            "candidate_day_count": len(enriched_rows),
            "active_wave_selection_day_count": len(active_wave_days),
            "post_wave_echo_guard_count": len(post_wave_days),
            "post_wave_echo_authority_family_count": sum(
                1 for row in post_wave_days if row["authority_family"] == "post_wave_echo_day"
            ),
            "aligned_or_displaced_inside_active_wave_count": sum(
                1 for row in active_wave_days if row["authority_family"] in {"aligned_selection_day", "displaced_selection_day"}
            ),
            "day_rows_csv": str(self.output_csv_path.relative_to(self.repo_root)),
            "authoritative_rule": (
                "post-wave echo days are already separable from active-wave selection days using simple recent order-flow state; the unresolved blocker now lives inside active-wave daily selection"
            ),
        }
        interpretation = [
            "V1.34FR checks whether the day-level add authority problem first needs a wave-state split before any finer daily ranking can make sense.",
            "It confirms that post-wave echo days can be separated cheaply from active-wave days, which narrows the remaining supervision burden to same-wave symbol selection.",
        ]
        return V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Report(
            summary=summary,
            day_rows=enriched_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fr_commercial_aerospace_add_wave_state_authority_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
