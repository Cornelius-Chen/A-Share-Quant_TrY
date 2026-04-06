from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134iq_commercial_aerospace_expanded_symbol_universe_carrier_search_audit_v1 import (
    V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Report:
        audit = V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "carrier_search_label": "priority_second_carrier_search_candidate",
                "direction": "promote_as_next_outside_named_second_carrier_search_target",
            },
            {
                "carrier_search_label": "formal_strength_watch_not_yet_carrier",
                "direction": "retain_as_watch_without_promotion",
            },
            {
                "carrier_search_label": "formal_noncandidate",
                "direction": "retain_as_noncandidate_and_do_not_force_formal_status_into_carrier_status",
            },
            {
                "carrier_search_label": "capital_true_selection",
                "direction": "continue_blocked_even_after_expanded_formal_search_until_new_comparison_evidence_is_labeled",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ir_commercial_aerospace_iq_expanded_carrier_direction_triage_v1",
            "priority_second_carrier_candidate_count": audit.summary["priority_second_carrier_candidate_count"],
            "authoritative_status": "retain_one_priority_outside_named_search_candidate_without_promoting_true_selection",
        }
        interpretation = [
            "V1.34IR converts the first expanded formal-universe carrier pass into direction.",
            "The route gains a next search target, but it still does not collapse the true-selection block into a promotion license.",
        ]
        return V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ir_commercial_aerospace_iq_expanded_carrier_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
