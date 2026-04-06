from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1 import (
    V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Report:
        audit = V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "ca_source_007",
                "direction": "retain_as_only_retained_symbol_named_hard_heat_source",
            },
            {
                "component": "ca_source_004_and_ca_source_012",
                "direction": "retain_as_discarded_theme_heat_lists_not_eligible_for_hard_counterpanel_expansion",
            },
            {
                "component": "ca_anchor_004",
                "direction": "retain_as_forward_manual_anchor_only_not_historical_hard_source",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_because_the_local_event_inventory_itself_does_not_supply_a_second_symbol_named_hard_heat_source",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jd_commercial_aerospace_jc_heat_source_direction_triage_v1",
            "retained_symbol_named_heat_source_count": audit.summary["retained_symbol_named_heat_source_count"],
            "second_symbol_named_heat_source_found": audit.summary["second_symbol_named_heat_source_found"],
            "authoritative_status": "retain_single_symbol_named_heat_source_stopline_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34JD turns event-source inventory into direction.",
            "The stack now knows the shortage is not just a candidate shortage; it is a retained hard heat-source shortage in the local event universe itself.",
        ]
        return V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jd_commercial_aerospace_jc_heat_source_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
