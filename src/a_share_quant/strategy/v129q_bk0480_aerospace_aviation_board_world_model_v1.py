from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: str | None) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V129QBK0480AerospaceAviationBoardWorldModelReport:
    summary: dict[str, Any]
    board_label_summary: dict[str, Any]
    world_model_prior: dict[str, Any]
    role_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "board_label_summary": self.board_label_summary,
            "world_model_prior": self.world_model_prior,
            "role_rows": self.role_rows,
            "interpretation": self.interpretation,
        }


class V129QBK0480AerospaceAviationBoardWorldModelAnalyzer:
    SECTOR_ID = "BK0480"

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

    def _board_rows(self) -> list[dict[str, str]]:
        return [row for row in self._load_csv(self.sector_snapshot_path) if row["sector_id"] == self.SECTOR_ID]

    def _stock_rows(self) -> list[dict[str, str]]:
        return [row for row in self._load_csv(self.stock_snapshot_path) if row["sector_id"] == self.SECTOR_ID]

    def _board_name(self, board_rows: list[dict[str, str]]) -> str:
        return board_rows[0]["sector_name"] if board_rows else self.SECTOR_ID

    def _board_metrics(self, rows: list[dict[str, str]]) -> dict[str, Any]:
        persistence = sum(_to_float(row["persistence"]) for row in rows) / len(rows)
        diffusion = sum(_to_float(row["diffusion"]) for row in rows) / len(rows)
        money = sum(_to_float(row["money_making"]) for row in rows) / len(rows)
        leader = sum(_to_float(row["leader_strength"]) for row in rows) / len(rows)
        relative = sum(_to_float(row["relative_strength"]) for row in rows) / len(rows)
        activity = sum(_to_float(row["activity"]) for row in rows) / len(rows)
        active_days = sum(
            1
            for row in rows
            if _to_float(row["persistence"]) > 0.5
            or _to_float(row["diffusion"]) > 0.5
            or _to_float(row["money_making"]) > 0.6
        )
        return {
            "row_count": len(rows),
            "active_days": active_days,
            "avg_persistence": round(persistence, 6),
            "avg_diffusion": round(diffusion, 6),
            "avg_money_making": round(money, 6),
            "avg_leader_strength": round(leader, 6),
            "avg_relative_strength": round(relative, 6),
            "avg_activity": round(activity, 6),
            "board_composite": round(
                (persistence + diffusion + money + leader + relative + activity) / 6.0,
                6,
            ),
        }

    def _role_rows(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row["symbol"], []).append(row)

        role_rows: list[dict[str, Any]] = []
        for symbol, items in grouped.items():
            avg_expected = sum(_to_float(item["expected_upside"]) for item in items) / len(items)
            avg_non_junk = sum(_to_float(item["non_junk_composite_score"]) for item in items) / len(items)
            avg_drive = sum(_to_float(item["drive_strength"]) for item in items) / len(items)
            avg_stability = sum(_to_float(item["stability"]) for item in items) / len(items)
            avg_liquidity = sum(_to_float(item["liquidity"]) for item in items) / len(items)
            avg_resonance = sum(_to_float(item["resonance"]) for item in items) / len(items)
            composite = (
                avg_expected
                + avg_non_junk
                + avg_drive
                + avg_stability
                + avg_liquidity
                + avg_resonance
            ) / 6.0

            role_rows.append(
                {
                    "symbol": symbol,
                    "row_count": len(items),
                    "avg_expected_upside": round(avg_expected, 6),
                    "avg_non_junk": round(avg_non_junk, 6),
                    "avg_drive_strength": round(avg_drive, 6),
                    "avg_stability": round(avg_stability, 6),
                    "avg_liquidity": round(avg_liquidity, 6),
                    "avg_resonance": round(avg_resonance, 6),
                    "symbol_composite": round(composite, 6),
                }
            )

        role_rows.sort(key=lambda row: row["symbol_composite"], reverse=True)
        for index, row in enumerate(role_rows):
            row["role_label"] = "stable_core_primary" if index == 0 else "high_quality_dual_core_support"
        return role_rows

    def analyze(self) -> V129QBK0480AerospaceAviationBoardWorldModelReport:
        board_rows = self._board_rows()
        stock_rows = self._stock_rows()
        board_name = self._board_name(board_rows)
        board_metrics = self._board_metrics(board_rows)
        role_rows = self._role_rows(stock_rows)

        primary = role_rows[0]["symbol"]
        support = role_rows[1]["symbol"] if len(role_rows) > 1 else role_rows[0]["symbol"]
        board_label_summary = {
            "board_name": board_name,
            "sector_id": self.SECTOR_ID,
            "board_character": "adjacent_aerospace_dual_core_board",
            "board_strength_posture": "narrower_adjacent_transfer_target_after_commercial_aerospace_freeze",
            "stable_core_primary": primary,
            "high_quality_dual_core_support": support,
        }
        world_model_prior = {
            "thesis": "BK0480 looks like the correct next transfer-preparation board because it is adjacent to commercial aerospace but structurally narrower, forcing portable grammar to prove itself on a dual-core aerospace board instead of a broad thematic impulse board.",
            "object_stack": [
                {"object_type": "board", "object_name": board_name, "role": "adjacent_aerospace_transfer_target"},
                {"object_type": "symbol", "object_name": primary, "role": "stable_core_primary"},
                {"object_type": "symbol", "object_name": support, "role": "high_quality_dual_core_support"},
            ],
            "risk_note": "The board is much narrower and less liquid than commercial aerospace, so future phases should assume lower breadth and avoid transferring commercial-aerospace aggression or chronology windows.",
            "next_phase_recommendation": "role_grammar",
        }
        summary = {
            "acceptance_posture": "freeze_v129q_bk0480_aerospace_aviation_board_world_model_v1",
            "board_name": board_name,
            "sector_id": self.SECTOR_ID,
            "next_phase": "role_grammar",
            "board_row_count": board_metrics["row_count"],
            "active_day_count": board_metrics["active_days"],
            "board_composite": board_metrics["board_composite"],
            "role_row_count": len(role_rows),
            "recommended_next_posture": "start_bk0480_role_grammar_from_dual_core_world_model_with_local_reset",
        }
        interpretation = [
            "V1.29Q starts the BK0480 worker from transfer preparation rather than from a raw queue entry.",
            "BK0480 presents as a narrower adjacent aerospace board with a dual-core structure led by 000738 and supported by 600118.",
            "That makes it a good first portability test because the method transfers, but the board semantics still need local relearning.",
        ]
        return V129QBK0480AerospaceAviationBoardWorldModelReport(
            summary=summary,
            board_label_summary=board_label_summary,
            world_model_prior=world_model_prior,
            role_rows=role_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129QBK0480AerospaceAviationBoardWorldModelReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129QBK0480AerospaceAviationBoardWorldModelAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129q_bk0480_aerospace_aviation_board_world_model_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
