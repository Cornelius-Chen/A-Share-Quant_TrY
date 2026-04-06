from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124KCommercialAerospaceCrossBoardForceProtocolReport:
    summary: dict[str, Any]
    layer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "layer_rows": self.layer_rows,
            "interpretation": self.interpretation,
        }


class V124KCommercialAerospaceCrossBoardForceProtocolAnalyzer:
    def analyze(self) -> V124KCommercialAerospaceCrossBoardForceProtocolReport:
        layer_rows = [
            {
                "layer_name": "layer_1_direct_board_owners",
                "definition": "direct 商业航天 board names that own the internal world_model and role_grammar",
                "members": ["002085", "000738", "600118"],
                "usage": [
                    "world_model_core",
                    "role_grammar_core",
                    "control_extraction_core",
                ],
            },
            {
                "layer_name": "layer_2_cross_board_propulsion_allies",
                "definition": "names outside the direct board label that can still act as real行情主力 and materially amplify 商业航天 trend expression",
                "members": [
                    {"symbol": "002565", "name": "顺灏股份"},
                    {"symbol": "002202", "name": "金风科技"},
                    {"symbol": "600783", "name": "鲁信创投"},
                ],
                "usage": [
                    "breadth_confirmation",
                    "theme_heat_confirmation",
                    "diffusion_support_audit",
                    "risk_off_spillover_monitor",
                ],
            },
            {
                "layer_name": "layer_3_adjacent_sector_support",
                "definition": "adjacent sector buckets that should still be watched because they share aerospace/defense/large-equipment capital rotation",
                "members": [
                    "BK0480:航天航空",
                    "BK0808:军民融合",
                    "BK0994:空间站概念",
                    "BK0814:大飞机",
                ],
                "usage": [
                    "shadow_sector_context",
                    "rotation_breadth_context",
                ],
            },
            {
                "layer_name": "layer_4_distant_sympathy_noise",
                "definition": "farther names whose movement may still echo the theme but should only affect breadth reading lightly",
                "members": [],
                "usage": ["weak_explanatory_only"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v124k_commercial_aerospace_cross_board_force_protocol_v1",
            "board_name": "商业航天",
            "protocol_shift": "from_single_board_core_only_to_dual_main_force_structure",
            "direct_core_count": 3,
            "cross_board_propulsion_count": 3,
            "authoritative_rule": "cross_board_propulsion_allies_are_not_noise_and_must_enter_breadth_and_diffusion_audit_but_must_not_replace_direct_board_owners_inside_role_grammar",
            "supersedes_interpretation_of": "v124j_commercial_aerospace_breadth_classification_protocol_v1",
            "recommended_next_posture": "start_role_grammar_with_layer_1_owners_and_layer_2_propulsion_allies_audited_in_parallel",
        }
        interpretation = [
            "V1.24K corrects an overly narrow reading of commercial aerospace breadth.",
            "Some names can sit outside the direct board label and still be genuine行情主力 for the commercial-aerospace move.",
            "The right response is not to demote them to noise, but to treat them as cross-board propulsion allies: important for breadth, heat, diffusion, and spillover, while still keeping the direct board owners responsible for internal role grammar.",
        ]
        return V124KCommercialAerospaceCrossBoardForceProtocolReport(
            summary=summary,
            layer_rows=layer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124KCommercialAerospaceCrossBoardForceProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124KCommercialAerospaceCrossBoardForceProtocolAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124k_commercial_aerospace_cross_board_force_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
