from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1 import (
    V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Report:
        audit = V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "contrast_name": "crowding_vs_weak_repair",
                "direction": "learn_crowding_as_symbol_level_strength_concentration_not_board_level_restart",
            },
            {
                "contrast_name": "high_beta_raw_only_rebound",
                "direction": "learn_high_beta_raw_only_rebound_as_separate_negative_label_not_crowding_not_unlock",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134hp_commercial_aerospace_ho_crowding_contrast_direction_triage_v1",
            "crowding_like_shelter_rebound_count": audit.summary["crowding_like_shelter_rebound_count"],
            "locked_board_weak_repair_count": audit.summary["locked_board_weak_repair_count"],
            "authoritative_status": "retain_crowding_vs_weak_repair_contrast_and_do_not_treat_crowded_symbol_strength_as_board_restart",
        }
        interpretation = [
            "V1.34HP converts the contrast into direction.",
            "Crowded shelter rebounds should be learned as concentrated symbol strength inside a still-locked board, not as a reason to reopen broad participation.",
        ]
        return V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HPCommercialAerospaceHOCrowdingContrastDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hp_commercial_aerospace_ho_crowding_contrast_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
