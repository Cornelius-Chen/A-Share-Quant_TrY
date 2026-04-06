from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134js_commercial_aerospace_heat_axis_counterpanel_expansion_audit_v1 import (
    V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Report:
        audit = V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "realized_heat_axis_seed",
                "direction": "retain_as_same_plane_singleton_reinforcement_only",
            },
            {
                "component": "forward_heat_axis_anchor",
                "direction": "retain_as_future_structure_not_current_counterpanel_thickener",
            },
            {
                "component": "hard_counterpanel",
                "direction": "continue_treating_as_singleton",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_while_counterpanel_remains_thin",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jt_commercial_aerospace_js_heat_axis_direction_triage_v1",
            "same_plane_counterpanel_expansion_ready_count": audit.summary["same_plane_counterpanel_expansion_ready_count"],
            "counterpanel_thickened_now": audit.summary["counterpanel_thickened_now"],
            "authoritative_status": "treat_the_heat_axis_branch_as_formalized_but_not_yet_counterpanel_thickening_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34JT converts the heat-axis expansion audit into direction.",
            "The branch is now explicit, but it still reinforces only the existing singleton hard counterpanel rather than expanding it into a second hard case.",
        ]
        return V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jt_commercial_aerospace_js_heat_axis_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
