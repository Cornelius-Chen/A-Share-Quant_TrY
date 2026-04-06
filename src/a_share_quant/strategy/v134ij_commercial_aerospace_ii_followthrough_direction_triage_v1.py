from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1 import (
    V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Report:
        audit = V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "followthrough_label": "persistent_symbol_followthrough_without_board_unlock",
                "direction": "retain_as_symbol_level_persistence_not_true_selection",
            },
            {
                "followthrough_label": "moderate_symbol_followthrough_without_board_unlock",
                "direction": "retain_as_supporting_evidence_not_promotion_license",
            },
            {
                "followthrough_label": "weak_or_nonpersistent_followthrough",
                "direction": "retain_as_negative_or_neutral_supporting_evidence",
            },
            {
                "followthrough_label": "capital_true_selection",
                "direction": "continue_blocked_even_after_followthrough_surface_exists",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ij_commercial_aerospace_ii_followthrough_direction_triage_v1",
            "symbol_count": audit.summary["symbol_count"],
            "persistent_followthrough_count": audit.summary["persistent_followthrough_count"],
            "authoritative_status": "retain_symbol_followthrough_as_its_own_supervision_layer_without_promoting_true_selection",
        }
        interpretation = [
            "V1.34IJ converts the first followthrough surface into direction.",
            "The key boundary remains intact: symbol persistence is useful to learn, but it still does not automatically authorize true selection.",
        ]
        return V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ij_commercial_aerospace_ii_followthrough_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
