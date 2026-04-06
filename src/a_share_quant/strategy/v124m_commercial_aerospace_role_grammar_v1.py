from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124MCommercialAerospaceRoleGrammarReport:
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


class V124MCommercialAerospaceRoleGrammarAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.universe_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_web_concept_universe_v1.csv"
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

    def _snapshot_support_map(self) -> dict[str, dict[str, Any]]:
        rows = self._load_csv(self.stock_snapshot_path)
        support: dict[str, dict[str, Any]] = {}
        for row in rows:
            symbol = row["symbol"]
            entry = support.setdefault(
                symbol,
                {
                    "sector_names": set(),
                    "row_count": 0,
                },
            )
            entry["sector_names"].add(row["sector_name"])
            entry["row_count"] += 1
        final: dict[str, dict[str, Any]] = {}
        for symbol, entry in support.items():
            final[symbol] = {
                "sector_names": sorted(entry["sector_names"]),
                "row_count": entry["row_count"],
                "support_posture": "snapshot_supported" if entry["row_count"] > 0 else "web_only",
            }
        return final

    def _assign_role(self, row: dict[str, str], support: dict[str, Any]) -> tuple[str, str]:
        group = row["group"]
        symbol = row["symbol"]

        if group == "正式组":
            if symbol == "002085":
                return "direct_liquid_leader", "board_internal_owner"
            if symbol in {"000738", "600118"}:
                return "direct_core_support", "board_internal_owner"
            return "direct_formal_support", "board_internal_owner"

        if group == "概念助推组":
            return "cross_board_propulsion_ally", "breadth_diffusion_driver"

        if group == "卖铲组":
            return "shovel_supplier_support", "supply_chain_confirmation"

        return "sentiment_mirror", "beta_mirror"

    def analyze(self) -> V124MCommercialAerospaceRoleGrammarReport:
        universe_rows = self._load_csv(self.universe_path)
        support_map = self._snapshot_support_map()

        role_rows: list[dict[str, Any]] = []
        for row in universe_rows:
            symbol = row["symbol"]
            support = support_map.get(
                symbol,
                {"sector_names": [], "row_count": 0, "support_posture": "web_only"},
            )
            role_label, structural_authority = self._assign_role(row, support)
            role_rows.append(
                {
                    "symbol": symbol,
                    "name": row["name"],
                    "group": row["group"],
                    "subgroup": row["subgroup"],
                    "role_label": role_label,
                    "structural_authority": structural_authority,
                    "snapshot_support_posture": support["support_posture"],
                    "snapshot_row_count": support["row_count"],
                    "snapshot_sector_names": support["sector_names"],
                    "rationale": row["rationale"],
                }
            )

        authority_rank = {
            "board_internal_owner": 0,
            "breadth_diffusion_driver": 1,
            "supply_chain_confirmation": 2,
            "beta_mirror": 3,
        }
        role_rows.sort(key=lambda row: (authority_rank[row["structural_authority"]], row["symbol"]))

        relative_structure_labels = [
            {
                "label_name": "internal_owner_stack",
                "members": [row["symbol"] for row in role_rows if row["structural_authority"] == "board_internal_owner"],
                "meaning": "these names are allowed to define internal board roles and later lawful controls",
            },
            {
                "label_name": "cross_board_propulsion_stack",
                "members": [row["symbol"] for row in role_rows if row["structural_authority"] == "breadth_diffusion_driver"],
                "meaning": "these names help confirm heat, breadth, and diffusion, but should not overwrite internal role grammar",
            },
            {
                "label_name": "shovel_confirmation_stack",
                "members": [row["symbol"] for row in role_rows if row["structural_authority"] == "supply_chain_confirmation"],
                "meaning": "these names are useful when validating whether the move is spreading through real supply chain demand",
            },
            {
                "label_name": "sentiment_mirror_stack",
                "members": [row["symbol"] for row in role_rows if row["structural_authority"] == "beta_mirror"],
                "meaning": "these names help read A-share style emotional extension and sympathy risk, not core ownership",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v124m_commercial_aerospace_role_grammar_v1",
            "board_name": "商业航天",
            "role_row_count": len(role_rows),
            "internal_owner_count": sum(1 for row in role_rows if row["structural_authority"] == "board_internal_owner"),
            "cross_board_propulsion_count": sum(1 for row in role_rows if row["structural_authority"] == "breadth_diffusion_driver"),
            "shovel_confirmation_count": sum(1 for row in role_rows if row["structural_authority"] == "supply_chain_confirmation"),
            "sentiment_mirror_count": sum(1 for row in role_rows if row["structural_authority"] == "beta_mirror"),
            "next_phase": "control_extraction",
            "recommended_next_posture": "derive_control_surface_from_internal_owner_stack_while_using_other_stacks_as_confirmation_layers",
        }
        interpretation = [
            "V1.24M turns the expanded commercial-aerospace universe into a role grammar instead of leaving it as a flat name list.",
            "The key move is to separate internal board ownership from cross-board propulsion, shovel confirmation, and sentiment mirrors.",
            "That keeps A-share breadth information alive without letting broad concept strength overwrite the board's internal mechanism layer.",
        ]
        return V124MCommercialAerospaceRoleGrammarReport(
            summary=summary,
            role_rows=role_rows,
            relative_structure_labels=relative_structure_labels,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124MCommercialAerospaceRoleGrammarReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124MCommercialAerospaceRoleGrammarAnalyzer(repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124m_commercial_aerospace_role_grammar_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
