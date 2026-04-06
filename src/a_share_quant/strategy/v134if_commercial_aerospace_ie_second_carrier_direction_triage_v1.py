from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ie_commercial_aerospace_second_carrier_case_search_audit_v1 import (
    V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Report:
        audit = V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "search_target": "second_carrier_case",
                "direction": "still_missing_continue_search_without_promoting_true_selection",
            },
            {
                "search_target": "000547",
                "direction": "retain_as_anchor_decoy_counterpanel_not_carrier",
            },
            {
                "search_target": "301306",
                "direction": "retain_as_follow_candidate_not_carrier",
            },
            {
                "search_target": "002361_and_300342",
                "direction": "retain_as_non_anchor_concentration_not_carrier",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134if_commercial_aerospace_ie_second_carrier_direction_triage_v1",
            "searched_symbol_count": audit.summary["searched_symbol_count"],
            "second_carrier_case_found": audit.summary["second_carrier_case_found"],
            "authoritative_status": "retain_negative_search_result_and_continue_blocking_true_selection_until_a_real_peer_carrier_case_exists",
        }
        interpretation = [
            "V1.34IF converts the second-carrier search result into direction.",
            "The correct next move is not to force a peer carrier but to keep the negative search result and preserve the block on true selection.",
        ]
        return V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134if_commercial_aerospace_ie_second_carrier_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
