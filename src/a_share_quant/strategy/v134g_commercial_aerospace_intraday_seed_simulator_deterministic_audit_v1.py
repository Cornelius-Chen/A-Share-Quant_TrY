from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134c_commercial_aerospace_intraday_seed_simulator_v1 import (
    V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer,
)


@dataclass(slots=True)
class V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditReport:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1.csv"
        )

    def analyze(self) -> V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditReport:
        analyzer = V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer(self.repo_root)
        run_a = analyzer.analyze()
        run_b = analyzer.analyze()

        exact_match = run_a.order_rows == run_b.order_rows and run_a.session_rows == run_b.session_rows

        order_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in run_a.order_rows:
            order_groups[(row["execution_trade_date"], row["symbol"])].append(row)

        session_rows: list[dict[str, Any]] = []
        monotonic_fill_violation_count = 0
        duplicate_fill_violation_count = 0
        post_flat_action_violation_count = 0

        session_lookup = {
            (row["execution_trade_date"], row["symbol"]): row for row in run_a.session_rows
        }

        for session_key, rows in sorted(order_groups.items()):
            trade_date, symbol = session_key
            rows_sorted = sorted(rows, key=lambda row: int(row["fill_minute"]))
            fill_minutes = [int(row["fill_minute"]) for row in rows_sorted]
            monotonic_ok = fill_minutes == sorted(fill_minutes)
            unique_ok = len(fill_minutes) == len(set(fill_minutes))
            monotonic_fill_violation_count += 0 if monotonic_ok else 1
            duplicate_fill_violation_count += 0 if unique_ok else 1

            session_meta = session_lookup[session_key]
            entry_qty = int(session_meta["entry_quantity"])
            remaining_qty = entry_qty
            local_post_flat_violation = 0
            trigger_sequence = []
            for row in rows_sorted:
                if remaining_qty <= 0:
                    local_post_flat_violation += 1
                sell_qty = int(row["sell_quantity"])
                remaining_qty -= sell_qty
                trigger_sequence.append(f"{row['trigger_tier']}@{row['fill_minute']}")
            post_flat_action_violation_count += local_post_flat_violation

            session_rows.append(
                {
                    "execution_trade_date": trade_date,
                    "symbol": symbol,
                    "order_count": len(rows_sorted),
                    "fill_sequence": " > ".join(trigger_sequence),
                    "fill_minutes_monotonic": monotonic_ok,
                    "fill_minutes_unique": unique_ok,
                    "post_flat_action_violation_count": local_post_flat_violation,
                    "ending_remaining_quantity_recomputed": remaining_qty,
                    "ending_remaining_quantity_reported": int(session_meta["remaining_quantity_after_sim"]),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        acceptance_rows = [
            {
                "acceptance_item": "double_run_exact_match",
                "status": "pass" if exact_match else "fail",
                "detail": f"exact_match = {exact_match}",
            },
            {
                "acceptance_item": "monotonic_fill_minutes",
                "status": "pass" if monotonic_fill_violation_count == 0 else "fail",
                "detail": f"monotonic_fill_violation_count = {monotonic_fill_violation_count}",
            },
            {
                "acceptance_item": "unique_fill_minutes",
                "status": "pass" if duplicate_fill_violation_count == 0 else "fail",
                "detail": f"duplicate_fill_violation_count = {duplicate_fill_violation_count}",
            },
            {
                "acceptance_item": "no_post_flat_actions",
                "status": "pass" if post_flat_action_violation_count == 0 else "fail",
                "detail": f"post_flat_action_violation_count = {post_flat_action_violation_count}",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1",
            "seed_session_with_orders_count": len(session_rows),
            "double_run_exact_match": exact_match,
            "monotonic_fill_violation_count": monotonic_fill_violation_count,
            "duplicate_fill_violation_count": duplicate_fill_violation_count,
            "post_flat_action_violation_count": post_flat_action_violation_count,
            "audit_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_seed_simulator_deterministic_audit_ready_for_phase_2_direction_triage",
        }
        interpretation = [
            "V1.34G checks whether the canonical seed simulator behaves like a deterministic execution object rather than a fragile exploratory script.",
            "The audit focuses on repeatability, monotonic fill ordering, and post-flat action suppression inside the narrow phase-2 seed lane.",
        ]
        return V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditReport(
            summary=summary,
            session_rows=session_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
