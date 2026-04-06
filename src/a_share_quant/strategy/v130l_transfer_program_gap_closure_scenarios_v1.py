from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130LTransferProgramGapClosureScenariosReport:
    summary: dict[str, Any]
    scenario_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "scenario_rows": self.scenario_rows,
            "interpretation": self.interpretation,
        }


class V130LTransferProgramGapClosureScenariosAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.freeze_path = repo_root / "reports" / "analysis" / "v130g_transfer_program_same_plane_support_freeze_v1.json"
        self.monitor_path = repo_root / "reports" / "analysis" / "v130k_transfer_program_watch_monitor_snapshot_v1.json"
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_gap_closure_scenarios_v1.csv"

    def analyze(self) -> V130LTransferProgramGapClosureScenariosReport:
        freeze_report = json.loads(self.freeze_path.read_text(encoding="utf-8"))
        monitor_report = json.loads(self.monitor_path.read_text(encoding="utf-8"))
        monitor_by_sector = {row["sector_id"]: row for row in monitor_report["monitor_rows"]}

        scenario_rows: list[dict[str, Any]] = []
        for row in freeze_report["candidate_rows"]:
            monitor_row = monitor_by_sector[row["sector_id"]]
            same_plane_gap = monitor_row["same_plane_symbol_gap"]
            board_gap = monitor_row["board_composite_gap"]
            bridge_block = bool(monitor_row["bridge_only_or_not_ready"])
            current_v6_symbols = row["v6_symbols"]
            current_v5_symbols = row["v5_symbols"]

            if row["sector_id"] == "BK0808":
                reopen_path = "add_one_more_v6_same_plane_symbol_and_clear_bridge_only_status"
                scenario_class = "nearest_reopen_candidate"
            elif same_plane_gap <= 1 and board_gap is not None and board_gap <= 0.03:
                reopen_path = "add_one_more_v6_same_plane_symbol_then_recheck_non_bridge_semantics"
                scenario_class = "same_plane_first_then_semantic_recheck"
            elif row["v6_symbol_count"] == 0:
                reopen_path = "establish_any_v6_same_plane_surface_before_doing_anything_else"
                scenario_class = "no_same_plane_surface"
            else:
                reopen_path = "needs_multi_step_gap_closure_not_single_action"
                scenario_class = "multi_step_gap_closure"

            scenario_rows.append(
                {
                    "sector_id": row["sector_id"],
                    "sector_name": row["sector_name"],
                    "scenario_class": scenario_class,
                    "current_v6_symbols": "|".join(current_v6_symbols),
                    "current_v5_symbols": "|".join(current_v5_symbols),
                    "same_plane_symbol_gap": same_plane_gap,
                    "board_composite_gap": board_gap,
                    "bridge_block": bridge_block,
                    "single_action_reopen_possible": row["sector_id"] == "BK0808",
                    "minimum_reopen_path": reopen_path,
                }
            )

        scenario_rows.sort(
            key=lambda item: (
                0 if item["single_action_reopen_possible"] else 1,
                item["same_plane_symbol_gap"],
                item["board_composite_gap"] if item["board_composite_gap"] is not None else 999.0,
                item["sector_id"],
            )
        )

        single_action_count = sum(1 for row in scenario_rows if row["single_action_reopen_possible"])
        summary = {
            "acceptance_posture": "freeze_v130l_transfer_program_gap_closure_scenarios_v1",
            "candidate_board_count": len(scenario_rows),
            "single_action_reopen_candidate_count": single_action_count,
            "nearest_reopen_sector_id": scenario_rows[0]["sector_id"] if scenario_rows else None,
            "authoritative_status": "freeze_transfer_program_and_rank_gap_closure_paths",
            "authoritative_rule": "do_not_reopen_a_board_worker_until_the_gap_closure_path_is_realized_in_local_same_plane_support_not_just_described_in_words",
        }
        interpretation = [
            "V1.30L turns the frozen watchlist into concrete gap-closure paths instead of passive waiting.",
            "BK0808 is still the closest candidate, but it remains blocked until one more v6 same-plane symbol appears and the bridge-only condition is cleared.",
        ]
        return V130LTransferProgramGapClosureScenariosReport(
            summary=summary,
            scenario_rows=scenario_rows,
            interpretation=interpretation,
        )

    def write_scenarios_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130LTransferProgramGapClosureScenariosReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130LTransferProgramGapClosureScenariosAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130l_transfer_program_gap_closure_scenarios_v1",
        result=result,
    )
    analyzer.write_scenarios_csv(result.scenario_rows)


if __name__ == "__main__":
    main()
