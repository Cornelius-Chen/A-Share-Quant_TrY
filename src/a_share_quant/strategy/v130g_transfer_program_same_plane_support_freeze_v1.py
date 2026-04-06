from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TARGETS = ["BK0808", "BK0715", "BK0994", "BK0814", "BK0490"]


@dataclass(slots=True)
class V130GTransferProgramSamePlaneSupportFreezeReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V130GTransferProgramSamePlaneSupportFreezeAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v6_sector_path = (
            repo_root
            / "data"
            / "derived"
            / "sector_snapshots"
            / "market_research_sector_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.v6_stock_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.v5_stock_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v5_carry_row_diversity_refresh.csv"
        )

    @staticmethod
    def _load_rows(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V130GTransferProgramSamePlaneSupportFreezeReport:
        v6_sector_rows = self._load_rows(self.v6_sector_path)
        v6_stock_rows = self._load_rows(self.v6_stock_path)
        v5_stock_rows = self._load_rows(self.v5_stock_path)

        candidate_rows = []
        for sector_id in TARGETS:
            sector_rows = [row for row in v6_sector_rows if row["sector_id"] == sector_id]
            v6_rows = [row for row in v6_stock_rows if row["sector_id"] == sector_id]
            v5_rows = [row for row in v5_stock_rows if row["sector_id"] == sector_id]
            sector_name = sector_rows[0]["sector_name"] if sector_rows else (v6_rows[0]["sector_name"] if v6_rows else (v5_rows[0]["sector_name"] if v5_rows else sector_id))
            v6_symbols = sorted({row["symbol"] for row in v6_rows})
            v5_symbols = sorted({row["symbol"] for row in v5_rows})
            same_plane_ready = len(v6_symbols) >= 2
            bridge_only = len(v6_symbols) == 1 and len(v5_symbols) >= 1
            composite = None
            if sector_rows:
                composite = round(
                    sum(
                        (
                            float(row["persistence"])
                            + float(row["diffusion"])
                            + float(row["money_making"])
                            + float(row["leader_strength"])
                            + float(row["relative_strength"])
                            + float(row["activity"])
                        )
                        / 6.0
                        for row in sector_rows
                    )
                    / len(sector_rows),
                    6,
                )
            if same_plane_ready:
                freeze_reason = "not_applicable"
            elif bridge_only:
                freeze_reason = "single_symbol_same_plane_support_only"
            else:
                freeze_reason = "no_same_plane_surface"
            candidate_rows.append(
                {
                    "sector_id": sector_id,
                    "sector_name": sector_name,
                    "v6_symbol_count": len(v6_symbols),
                    "v6_symbols": v6_symbols,
                    "v5_symbol_count": len(v5_symbols),
                    "v5_symbols": v5_symbols,
                    "v6_sector_row_count": len(sector_rows),
                    "v6_board_composite": composite,
                    "same_plane_ready": same_plane_ready,
                    "bridge_only": bridge_only,
                    "freeze_reason": freeze_reason,
                }
            )

        same_plane_ready_count = sum(row["same_plane_ready"] for row in candidate_rows)
        summary = {
            "acceptance_posture": "freeze_v130g_transfer_program_same_plane_support_freeze_v1",
            "candidate_board_count": len(candidate_rows),
            "same_plane_ready_count": same_plane_ready_count,
            "bridge_only_count": sum(row["bridge_only"] for row in candidate_rows),
            "authoritative_status": "freeze_transfer_program_until_a_new_board_has_multi_symbol_same_plane_support",
            "authoritative_rule": "do_not_open_new_board_workers_when_the_destination_surface_collapses_to_single_symbol_or_cross_version_bridge_only",
            "recommended_next_posture": "pause_board_transfer_and_wait_for_richer_same_plane_local_support",
        }
        interpretation = [
            "V1.30G re-checks the post-BK0480 queue instead of blindly advancing into thinner boards.",
            "No remaining shadow target has multi-symbol same-plane support, so opening another board worker would degrade transfer discipline into single-symbol pseudo-board research.",
        ]
        return V130GTransferProgramSamePlaneSupportFreezeReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130GTransferProgramSamePlaneSupportFreezeReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130GTransferProgramSamePlaneSupportFreezeAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130g_transfer_program_same_plane_support_freeze_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
