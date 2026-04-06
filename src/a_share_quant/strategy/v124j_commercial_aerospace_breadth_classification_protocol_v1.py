from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124JCommercialAerospaceBreadthClassificationProtocolReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    manual_watchlist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "manual_watchlist_rows": self.manual_watchlist_rows,
            "interpretation": self.interpretation,
        }


class V124JCommercialAerospaceBreadthClassificationProtocolAnalyzer:
    def analyze(self) -> V124JCommercialAerospaceBreadthClassificationProtocolReport:
        tier_rows = [
            {
                "tier_name": "tier_1_direct_board_driver",
                "definition": "symbols that sit inside the direct 商业航天 board worker and are allowed to shape world_model, role_grammar, and later lawful controls",
                "symbols": ["002085", "000738", "600118"],
                "source_posture": "direct_snapshot_supported",
                "execution_authority": "full_research_authority",
            },
            {
                "tier_name": "tier_2_adjacent_same_engine_support",
                "definition": "symbols and sectors that are structurally adjacent enough to audit as shadow support, but not yet allowed to redefine the board itself",
                "symbols": ["BK0480:航天航空", "BK0808:军民融合", "BK0994:空间站概念", "BK0814:大飞机"],
                "source_posture": "adjacent_shadow_supported",
                "execution_authority": "shadow_context_only",
            },
            {
                "tier_name": "tier_3_thematic_propagation_concepts",
                "definition": "broad concept names that may rise with the theme through sentiment, funding rotation, or narration, but should not be mistaken for direct board drivers",
                "symbols": [],
                "source_posture": "manual_watchlist_only",
                "execution_authority": "watchlist_explanatory_only",
            },
            {
                "tier_name": "tier_4_distant_sympathy_names",
                "definition": "farther names whose linkage is mostly market narration or risk-on sympathy; they may help breadth reading but must not drive primary board controls",
                "symbols": [],
                "source_posture": "manual_watchlist_only",
                "execution_authority": "breadth_noise_only",
            },
        ]

        manual_watchlist_rows = [
            {
                "symbol": "002565",
                "name": "顺灏股份",
                "user_noted_role": "broad_concept_participant",
                "initial_classification": "tier_3_thematic_propagation_concepts",
                "reason": "mentioned as concept-linked but not currently part of the direct supported 商业航天 snapshot core",
            },
            {
                "symbol": "002202",
                "name": "金风科技",
                "user_noted_role": "broad_concept_participant",
                "initial_classification": "tier_3_thematic_propagation_concepts",
                "reason": "should be tracked as narrative breadth until direct chain evidence is established locally",
            },
            {
                "symbol": "600783",
                "name": "鲁信创投",
                "user_noted_role": "broad_concept_participant",
                "initial_classification": "tier_3_thematic_propagation_concepts",
                "reason": "should begin as propagation-watchlist rather than direct board driver",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v124j_commercial_aerospace_breadth_classification_protocol_v1",
            "board_name": "商业航天",
            "tier_count": 4,
            "direct_driver_count": 3,
            "manual_watchlist_count": 3,
            "key_rule": "do_not_let_tier_3_or_tier_4_names_redefine_board_world_model_before_tier_1_and_tier_2_are_stable",
            "recommended_next_posture": "run_role_grammar_on_tier_1_direct_drivers_while_keeping_broad_concept_names_in_watchlist_only",
        }
        interpretation = [
            "V1.24J prevents the commercial-aerospace worker from being polluted by broad concept sprawl at the very start.",
            "The direct board worker should be built from tier-1 names first, then audited against adjacent tier-2 support sectors, while tier-3 and tier-4 names remain explanatory watchlists.",
            "This keeps broad thematic names visible without letting them hijack the mechanism-learning unit too early.",
        ]
        return V124JCommercialAerospaceBreadthClassificationProtocolReport(
            summary=summary,
            tier_rows=tier_rows,
            manual_watchlist_rows=manual_watchlist_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124JCommercialAerospaceBreadthClassificationProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124JCommercialAerospaceBreadthClassificationProtocolAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124j_commercial_aerospace_breadth_classification_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
