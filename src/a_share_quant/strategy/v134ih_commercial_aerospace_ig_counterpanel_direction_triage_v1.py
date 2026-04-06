from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1 import (
    V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Report:
        audit = V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "target": "hard_counterpanel",
                "direction": "still_single_case_keep_000547_as_only_hard_anchor_decoy_reference",
            },
            {
                "target": "soft_decoy_only_candidates",
                "direction": "retain_as_soft_only_and_do_not_promote_without_hard_heat_evidence",
            },
            {
                "target": "carrier_and_follow_cases",
                "direction": "keep_outside_counterpanel_and_do_not_confuse_them_with_decoy_labels",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ih_commercial_aerospace_ig_counterpanel_direction_triage_v1",
            "searched_symbol_count": audit.summary["searched_symbol_count"],
            "second_hard_counterpanel_found": audit.summary["second_hard_counterpanel_found"],
            "authoritative_status": "retain_single_hard_counterpanel_case_and_continue_blocking_thicker_counterpanel_promotion",
        }
        interpretation = [
            "V1.34IH converts the counterpanel search result into direction.",
            "The immediate lesson is still conservative: the system has one hard anchor/decoy case and should not inflate softer evidence into a fake counterpanel.",
        ]
        return V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ih_commercial_aerospace_ig_counterpanel_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
