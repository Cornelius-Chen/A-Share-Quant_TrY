from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ju_commercial_aerospace_carrier_follow_search_expansion_audit_v1 import (
    V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Report:
        audit = V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "linked_carrier_case",
                "direction": "retain_as_same_plane_carrier_reinforcement_only",
            },
            {
                "component": "linked_follow_case",
                "direction": "retain_as_same_plane_follow_reinforcement_only",
            },
            {
                "component": "outside_named_supply_chain_watch",
                "direction": "retain_as_future_watch_without_symbol_promotion",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_while_branch_remains_reinforcement_only",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jv_commercial_aerospace_ju_carrier_follow_direction_triage_v1",
            "linked_local_case_count": audit.summary["linked_local_case_count"],
            "outside_named_watch_count": audit.summary["outside_named_watch_count"],
            "branch_promotive": audit.summary["branch_promotive"],
            "authoritative_status": "treat_carrier_follow_search_as_formalized_same_plane_reinforcement_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34JV converts the carrier-follow branch into direction.",
            "The branch is now explicit and useful, but it still reinforces existing carrier/follow readings rather than opening any true-selection authority.",
        ]
        return V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jv_commercial_aerospace_ju_carrier_follow_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
