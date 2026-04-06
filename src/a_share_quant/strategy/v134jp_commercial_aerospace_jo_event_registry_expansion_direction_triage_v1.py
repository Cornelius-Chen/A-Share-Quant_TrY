from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jo_commercial_aerospace_decisive_event_registry_expansion_utility_audit_v1 import (
    V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Report:
        audit = V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "broader_symbol_pool_expander",
                "direction": "promote_as_first_decisive_registry_symbol_expansion_branch",
            },
            {
                "component": "heat_axis_and_counterpanel_expander",
                "direction": "retain_as_second_decisive_registry_expansion_branch",
            },
            {
                "component": "carrier_follow_search_expander",
                "direction": "retain_as_parallel_registry_branch_for_future_carrier_support",
            },
            {
                "component": "event_context_alignment_and_risk_anchors",
                "direction": "retain_as_environment_alignment_support_only",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_during_registry_expansion_stage",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jp_commercial_aerospace_jo_event_registry_expansion_direction_triage_v1",
            "retained_registry_row_count": audit.summary["retained_registry_row_count"],
            "broader_symbol_pool_expander_count": audit.summary["broader_symbol_pool_expander_count"],
            "capital_true_selection_blocked": True,
            "authoritative_status": "treat_broader_symbol_pool_expansion_from_the_decisive_registry_as_the_first_live_same_plane_branch_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34JP converts decisive-registry utility classes into branch order.",
            "The first live branch should be broader symbol-pool expansion because it directly addresses the current lack of additional same-plane named evidence, while true-selection promotion remains blocked.",
        ]
        return V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jp_commercial_aerospace_jo_event_registry_expansion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
