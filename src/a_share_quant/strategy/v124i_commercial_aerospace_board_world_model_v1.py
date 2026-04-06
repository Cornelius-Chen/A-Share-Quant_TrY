from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V124ICommercialAerospaceBoardWorldModelReport:
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


class V124ICommercialAerospaceBoardWorldModelAnalyzer:
    BOARD_NAME = "商业航天"
    SECTOR_ID = "BK0963"

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

    def _board_metrics(self) -> dict[str, Any]:
        rows = [
            row
            for row in self._load_csv(self.sector_snapshot_path)
            if row["sector_id"] == self.SECTOR_ID and row["sector_name"] == self.BOARD_NAME
        ]
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

    def _symbol_roles(self) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self._load_csv(self.stock_snapshot_path)
            if row["sector_name"] == self.BOARD_NAME
        ]
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

            if len(items) >= 100 and avg_liquidity >= 0.5 and avg_drive >= 0.5:
                role_label = "primary_liquid_leader"
            elif len(items) >= 20 and avg_stability >= 0.65 and avg_resonance >= 0.55:
                role_label = "stable_core_support"
            else:
                role_label = "high_quality_sparse_alt"

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
                    "role_label": role_label,
                }
            )

        role_rows.sort(key=lambda row: row["symbol_composite"], reverse=True)
        return role_rows

    def analyze(self) -> V124ICommercialAerospaceBoardWorldModelReport:
        board_metrics = self._board_metrics()
        role_rows = self._symbol_roles()

        role_map = {row["role_label"]: row["symbol"] for row in role_rows}
        board_label_summary = {
            "board_name": self.BOARD_NAME,
            "sector_id": self.SECTOR_ID,
            "board_character": "high_activity_diffusion_capable_aerospace_theme",
            "board_strength_posture": "best_next_board_after_cpo_freeze",
            "primary_liquid_leader": role_map.get("primary_liquid_leader", role_rows[0]["symbol"]),
            "stable_core_support": role_map.get("stable_core_support", role_rows[min(1, len(role_rows) - 1)]["symbol"]),
            "high_quality_sparse_alt": role_map.get("high_quality_sparse_alt", role_rows[-1]["symbol"]),
        }
        world_model_prior = {
            "thesis": "商业航天 currently looks like the cleanest next portability target because it combines strong activity, broad active-day coverage, and a role structure that is not purely single-symbol fragile.",
            "object_stack": [
                {
                    "object_type": "board",
                    "object_name": self.BOARD_NAME,
                    "role": "diffusion_capable_main_board",
                },
                {
                    "object_type": "symbol",
                    "object_name": board_label_summary["primary_liquid_leader"],
                    "role": "primary_liquid_leader",
                },
                {
                    "object_type": "symbol",
                    "object_name": board_label_summary["stable_core_support"],
                    "role": "stable_core_support",
                },
                {
                    "object_type": "symbol",
                    "object_name": board_label_summary["high_quality_sparse_alt"],
                    "role": "high_quality_sparse_alt",
                },
            ],
            "risk_note": "activity is unusually high, so later phases should explicitly watch for hype-driven false diffusion and sparse-symbol leadership concentration.",
            "next_phase_recommendation": "role_grammar",
        }
        summary = {
            "acceptance_posture": "freeze_v124i_commercial_aerospace_board_world_model_v1",
            "board_name": self.BOARD_NAME,
            "sector_id": self.SECTOR_ID,
            "next_phase": "role_grammar",
            "board_row_count": board_metrics["row_count"],
            "active_day_count": board_metrics["active_days"],
            "board_composite": board_metrics["board_composite"],
            "recommended_next_posture": "start_commercial_aerospace_role_grammar_with_current_symbol_triplet",
        }
        interpretation = [
            "V1.24I starts the next board worker instead of stopping at queue expansion.",
            "Commercial aerospace enters with one liquid primary leader, one stable core support name, and one sparse but high-quality alternate.",
            "That is enough structure to move into role grammar without pretending the board is already solved.",
        ]
        return V124ICommercialAerospaceBoardWorldModelReport(
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
    result: V124ICommercialAerospaceBoardWorldModelReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124ICommercialAerospaceBoardWorldModelAnalyzer(repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124i_commercial_aerospace_board_world_model_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
