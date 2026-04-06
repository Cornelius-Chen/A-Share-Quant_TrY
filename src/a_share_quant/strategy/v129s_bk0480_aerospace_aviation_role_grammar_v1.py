from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129SBK0480AerospaceAviationRoleGrammarReport:
    summary: dict[str, Any]
    role_rows: list[dict[str, Any]]
    relative_structure_labels: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_rows": self.role_rows,
            "relative_structure_labels": self.relative_structure_labels,
            "interpretation": self.interpretation,
        }


class V129SBK0480AerospaceAviationRoleGrammarAnalyzer:
    SECTOR_ID = "BK0480"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stock_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.world_model_path = (
            repo_root / "reports" / "analysis" / "v129q_bk0480_aerospace_aviation_board_world_model_v1.json"
        )

    def _load_snapshot_rows(self) -> list[dict[str, str]]:
        with self.stock_snapshot_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return [row for row in rows if row["sector_id"] == self.SECTOR_ID]

    def analyze(self) -> V129SBK0480AerospaceAviationRoleGrammarReport:
        world_model = json.loads(self.world_model_path.read_text(encoding="utf-8"))
        board_name = world_model["summary"]["board_name"]
        snapshot_rows = self._load_snapshot_rows()

        by_symbol: dict[str, list[dict[str, str]]] = {}
        for row in snapshot_rows:
            by_symbol.setdefault(row["symbol"], []).append(row)

        role_rows: list[dict[str, Any]] = []
        for symbol, rows in sorted(by_symbol.items()):
            world_role = next(item["role"] for item in world_model["world_model_prior"]["object_stack"] if item["object_type"] == "symbol" and item["object_name"] == symbol)
            if world_role == "stable_core_primary":
                role_label = "stable_core_primary"
                structural_authority = "board_internal_owner"
            else:
                role_label = "high_quality_dual_core_support"
                structural_authority = "board_internal_owner"

            role_rows.append(
                {
                    "symbol": symbol,
                    "role_label": role_label,
                    "structural_authority": structural_authority,
                    "snapshot_row_count": len(rows),
                    "snapshot_sector_names": sorted({row["sector_name"] for row in rows}),
                    "transfer_reset_posture": "local_snapshot_supported",
                    "rationale": (
                        "BK0480 starts from a narrow dual-core local role surface; no confirmation or mirror layers are authorized yet "
                        "until a local universe expansion is justified by BK0480-native evidence."
                    ),
                }
            )

        role_rows.sort(key=lambda row: row["snapshot_row_count"], reverse=True)

        relative_structure_labels = [
            {
                "label_name": "internal_owner_stack",
                "members": [row["symbol"] for row in role_rows],
                "meaning": "these two symbols are the only BK0480-local owners currently authorized to define role semantics",
            },
            {
                "label_name": "confirmation_stack",
                "members": [],
                "meaning": "intentionally empty at kickoff; no commercial-aerospace confirmation layer is allowed to leak into BK0480",
            },
            {
                "label_name": "mirror_stack",
                "members": [],
                "meaning": "intentionally empty at kickoff; sympathy names require BK0480-local evidence before admission",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129s_bk0480_aerospace_aviation_role_grammar_v1",
            "board_name": board_name,
            "sector_id": self.SECTOR_ID,
            "role_row_count": len(role_rows),
            "internal_owner_count": len(role_rows),
            "confirmation_count": 0,
            "mirror_count": 0,
            "next_phase": "control_seed_extraction",
            "recommended_next_posture": "derive_a_minimal_control_seed_from_the_dual_core_only_then_reassess_local_expansion",
        }
        interpretation = [
            "V1.29S keeps BK0480 deliberately narrow at kickoff: two internal owners and no borrowed confirmation or mirror layers.",
            "This enforces the transfer boundary by making BK0480 prove its own local structure before any broader universe expansion.",
        ]
        return V129SBK0480AerospaceAviationRoleGrammarReport(
            summary=summary,
            role_rows=role_rows,
            relative_structure_labels=relative_structure_labels,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129SBK0480AerospaceAviationRoleGrammarReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129SBK0480AerospaceAviationRoleGrammarAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129s_bk0480_aerospace_aviation_role_grammar_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
