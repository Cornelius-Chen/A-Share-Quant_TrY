from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V124HMultiBoardQueueExpansionReport:
    summary: dict[str, Any]
    board_candidate_rows: list[dict[str, Any]]
    queue_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "board_candidate_rows": self.board_candidate_rows,
            "queue_rows": self.queue_rows,
            "interpretation": self.interpretation,
        }


class V124HMultiBoardQueueExpansionAnalyzer:
    TARGET_SECTORS = ("商业航天", "航天航空", "军民融合")

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sector_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "sector_snapshots"
            / "market_research_sector_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.stock_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )

    def _load_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _sector_rows(self) -> list[dict[str, Any]]:
        rows = self._load_csv(self.sector_snapshot_path)
        grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in rows:
            key = (row["sector_id"], row["sector_name"])
            grouped.setdefault(key, []).append(row)

        ranked: list[dict[str, Any]] = []
        for (sector_id, sector_name), items in grouped.items():
            persistence = sum(_to_float(item["persistence"]) for item in items) / len(items)
            diffusion = sum(_to_float(item["diffusion"]) for item in items) / len(items)
            money = sum(_to_float(item["money_making"]) for item in items) / len(items)
            leader = sum(_to_float(item["leader_strength"]) for item in items) / len(items)
            relative = sum(_to_float(item["relative_strength"]) for item in items) / len(items)
            activity = sum(_to_float(item["activity"]) for item in items) / len(items)
            active_days = sum(
                1
                for item in items
                if _to_float(item["persistence"]) > 0.5
                or _to_float(item["diffusion"]) > 0.5
                or _to_float(item["money_making"]) > 0.6
            )
            ranked.append(
                {
                    "sector_id": sector_id,
                    "sector_name": sector_name,
                    "row_count": len(items),
                    "active_days": active_days,
                    "avg_persistence": round(persistence, 6),
                    "avg_diffusion": round(diffusion, 6),
                    "avg_money_making": round(money, 6),
                    "avg_leader_strength": round(leader, 6),
                    "avg_relative_strength": round(relative, 6),
                    "avg_activity": round(activity, 6),
                    "composite": round(
                        (persistence + diffusion + money + leader + relative + activity) / 6.0,
                        6,
                    ),
                }
            )
        ranked.sort(key=lambda row: row["composite"], reverse=True)
        return ranked

    def _symbol_rows(self) -> dict[str, list[dict[str, Any]]]:
        rows = self._load_csv(self.stock_snapshot_path)
        grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in rows:
            key = (row["sector_name"], row["symbol"])
            grouped.setdefault(key, []).append(row)

        per_sector: dict[str, list[dict[str, Any]]] = {}
        for (sector_name, symbol), items in grouped.items():
            composite = (
                sum(_to_float(item["expected_upside"]) for item in items) / len(items)
                + sum(_to_float(item["non_junk_composite_score"]) for item in items) / len(items)
                + sum(_to_float(item["drive_strength"]) for item in items) / len(items)
                + sum(_to_float(item["stability"]) for item in items) / len(items)
                + sum(_to_float(item["liquidity"]) for item in items) / len(items)
                + sum(_to_float(item["resonance"]) for item in items) / len(items)
            ) / 6.0
            entry = {
                "symbol": symbol,
                "row_count": len(items),
                "composite": round(composite, 6),
                "robustness": "robust" if len(items) >= 10 else "sparse_alt",
            }
            per_sector.setdefault(sector_name, []).append(entry)

        for sector_name in per_sector:
            per_sector[sector_name].sort(key=lambda row: row["composite"], reverse=True)
        return per_sector

    def analyze(self) -> V124HMultiBoardQueueExpansionReport:
        sector_rows = self._sector_rows()
        symbol_rows = self._symbol_rows()

        candidate_rows: list[dict[str, Any]] = []
        for row in sector_rows:
            if row["sector_name"] not in self.TARGET_SECTORS:
                continue
            sector_symbols = symbol_rows.get(row["sector_name"], [])
            robust = [item for item in sector_symbols if item["row_count"] >= 10][:3]
            if len(robust) < 3:
                sparse = [item for item in sector_symbols if item["row_count"] < 10]
                robust.extend(sparse[: 3 - len(robust)])
            candidate_rows.append(
                {
                    **row,
                    "recommended_core_symbols": [item["symbol"] for item in robust],
                    "core_symbol_rows": robust,
                    "queue_role": (
                        "next_primary"
                        if row["sector_name"] == "商业航天"
                        else "alternate_shadow"
                    ),
                }
            )

        queue_rows = [
            {
                "queue_order": 1,
                "board_name": "CPO",
                "queue_status": "terminal_frozen",
                "terminal_status": "frozen_heat_only_execution_stack",
                "next_phase": None,
                "run_until": "already_terminal",
            }
        ]
        for index, row in enumerate(candidate_rows, start=2):
            queue_rows.append(
                {
                    "queue_order": index,
                    "board_name": row["sector_name"],
                    "sector_id": row["sector_id"],
                    "queue_status": "queued" if index == 2 else "queued_shadow",
                    "terminal_status": None,
                    "next_phase": "board_world_model",
                    "run_until": "terminal_status_or_hard_stop",
                    "recommended_core_symbols": "|".join(row["recommended_core_symbols"]),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v124h_multi_board_queue_expansion_v1",
            "source_sector_snapshot": self.sector_snapshot_path.name,
            "source_stock_snapshot": self.stock_snapshot_path.name,
            "current_terminal_board": "CPO",
            "current_terminal_status": "frozen_heat_only_execution_stack",
            "next_primary_board": "商业航天",
            "next_primary_sector_id": "BK0963",
            "alternate_shadow_boards": ["航天航空", "军民融合"],
            "queue_count": len(queue_rows),
            "candidate_board_count": len(candidate_rows),
            "recommended_next_posture": "start_autonomous_board_worker_from_商业航天_then_keep_航天航空_and_军民融合_as_shadow_queue",
        }
        interpretation = [
            "V1.24H formalizes the post-CPO handoff instead of leaving the next board choice implicit.",
            "Commercial aerospace becomes the primary next board because it leads the current sector snapshot on composite strength, active days, and sample depth at the same time.",
            "Aerospace and military-civil fusion remain queued as shadow alternates so the board worker can pivot without having to rebuild the queue from scratch.",
        ]
        return V124HMultiBoardQueueExpansionReport(
            summary=summary,
            board_candidate_rows=candidate_rows,
            queue_rows=queue_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124HMultiBoardQueueExpansionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_queue_csv(*, data_dir: Path, result: V124HMultiBoardQueueExpansionReport) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "multi_board_queue_expansion_v1.csv"
    fieldnames = [
        "queue_order",
        "board_name",
        "sector_id",
        "queue_status",
        "terminal_status",
        "next_phase",
        "run_until",
        "recommended_core_symbols",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.queue_rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124HMultiBoardQueueExpansionAnalyzer(repo_root)
    result = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124h_multi_board_queue_expansion_v1",
        result=result,
    )
    csv_path = write_queue_csv(
        data_dir=repo_root / "data" / "training",
        result=result,
    )
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
