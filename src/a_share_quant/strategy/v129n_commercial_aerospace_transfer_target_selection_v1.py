from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129NCommercialAerospaceTransferTargetSelectionReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V129NCommercialAerospaceTransferTargetSelectionAnalyzer:
    BOARD_LABELS = {
        "BK0963": "商业航天",
        "BK0480": "航天航空",
        "BK0808": "军民融合",
    }

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.queue_path = repo_root / "reports" / "analysis" / "v124h_multi_board_queue_expansion_v1.json"
        self.portability_path = repo_root / "reports" / "analysis" / "v128k_commercial_aerospace_portability_packaging_v1.json"
        self.governance_path = repo_root / "reports" / "analysis" / "v129m_commercial_aerospace_klm_governance_packaging_triage_v1.json"
        self.control_surface_path = repo_root / "reports" / "analysis" / "v124w_commercial_aerospace_control_extraction_v1.json"

    def analyze(self) -> V129NCommercialAerospaceTransferTargetSelectionReport:
        queue = json.loads(self.queue_path.read_text(encoding="utf-8"))
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))
        governance = json.loads(self.governance_path.read_text(encoding="utf-8"))
        control_surface = json.loads(self.control_surface_path.read_text(encoding="utf-8"))

        primary_symbols = {
            row["symbol"] for row in control_surface["eligibility_rows"] if row["control_action"] == "eligibility_authority"
        }

        candidate_rows: list[dict[str, Any]] = []
        for row in queue["board_candidate_rows"]:
            if row["sector_id"] == "BK0963":
                continue

            sector_id = row["sector_id"]
            board_name = self.BOARD_LABELS.get(sector_id, sector_id)
            board_core = set(row.get("recommended_core_symbols", []))
            overlap_count = len(primary_symbols & board_core)
            overlap_ratio = overlap_count / max(len(primary_symbols), 1)

            if sector_id == "BK0480":
                archetype_fit = 0.82
                thematic_noise_risk = 0.28
                verdict = "recommended_primary_transfer_target"
                why = (
                    "Closest adjacent aerospace board, retains direct overlap with the commercial-aerospace authority surface, "
                    "and is narrow enough to test portable grammar without collapsing into a mixed concept basket."
                )
            else:
                archetype_fit = 0.41
                thematic_noise_risk = 0.72
                verdict = "shadow_only_later_transfer_target"
                why = (
                    "Broader mixed-theme board with weaker semantic alignment; keep queued as a later shadow transfer target "
                    "after a cleaner adjacent-board validation."
                )

            transfer_readiness = (
                0.45 * overlap_ratio
                + 0.35 * float(row["composite"])
                + 0.20 * archetype_fit
                - 0.10 * thematic_noise_risk
            )
            candidate_rows.append(
                {
                    "sector_id": sector_id,
                    "board_name": board_name,
                    "queue_role": row["queue_role"],
                    "composite": row["composite"],
                    "active_days": row["active_days"],
                    "recommended_core_symbols": sorted(board_core),
                    "commercial_aerospace_primary_overlap_count": overlap_count,
                    "commercial_aerospace_primary_overlap_ratio": round(overlap_ratio, 6),
                    "archetype_fit_score": archetype_fit,
                    "thematic_noise_risk": thematic_noise_risk,
                    "transfer_readiness_score": round(transfer_readiness, 6),
                    "verdict": verdict,
                    "reason": why,
                }
            )

        candidate_rows.sort(key=lambda item: item["transfer_readiness_score"], reverse=True)

        blocked_rows = [
            {
                "blocked_direction": "direct_rule_clone",
                "blocked_item": "tail_weakdrift_full",
                "reason": "Rule names and exact replay geometry are commercial-aerospace local semantics, not portable execution grammar.",
            },
            {
                "blocked_direction": "chronology_clone",
                "blocked_item": "main_window_20260112_to_20260212_and_post_window_after_20260212",
                "reason": "Local chronology windows must be relearned on the destination board.",
            },
            {
                "blocked_direction": "symbol_fact_clone",
                "blocked_item": "688568/600118/600879_help_and_300342/000738/601698_pressure",
                "reason": "Symbol pressure maps are board-local facts and cannot be transplanted.",
            },
            {
                "blocked_direction": "archetype_mixing",
                "blocked_item": "commercial_aerospace_thematic_impulse_to_military_civil_fusion",
                "reason": "Transfer must not mix a catalyst-concentrated thematic-impulse archetype into a broader mixed-concept board.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129n_commercial_aerospace_transfer_target_selection_v1",
            "current_frozen_board": "commercial_aerospace",
            "current_frozen_status": governance["summary"]["authoritative_status"],
            "portable_methodology_status": portability["summary"]["authoritative_output"],
            "recommended_primary_transfer_target": "BK0480",
            "recommended_primary_transfer_board_name": self.BOARD_LABELS["BK0480"],
            "shadow_later_target": "BK0808",
            "selection_rule": "choose_the_closest_adjacent_board_that_maximizes_portable_grammar_fit_without_mixing_archetypes",
        }
        interpretation = [
            "V1.29N converts transfer preparation from a vague next-step into an explicit board-selection decision.",
            "BK0480 is preferred because it is adjacent enough to validate portable grammar but narrower and cleaner than BK0808.",
        ]
        return V129NCommercialAerospaceTransferTargetSelectionReport(
            summary=summary,
            candidate_rows=candidate_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129NCommercialAerospaceTransferTargetSelectionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129NCommercialAerospaceTransferTargetSelectionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129n_commercial_aerospace_transfer_target_selection_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
