from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jq_commercial_aerospace_broader_symbol_pool_materialization_gap_audit_v1 import (
    V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Report:
        audit = V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "broader_symbol_pool_expander_branch",
                "direction": "retain_as_first_live_branch_but_do_not_claim_materialized_pool",
            },
            {
                "component": "local_security_master",
                "direction": "treat_as_current_materialization_blocker",
            },
            {
                "component": "heat_axis_and_counterpanel_expander",
                "direction": "retain_as_next_parallel_branch_while_symbol_materialization_is_blocked",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_because_broader_symbol_pool_is_not_yet_materialized",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jr_commercial_aerospace_jq_symbol_pool_gap_direction_triage_v1",
            "materialized_symbol_count": audit.summary["materialized_symbol_count"],
            "authoritative_status": "treat_name_to_symbol_coverage_as_the_current_blocker_for_broader_symbol_pool_expansion_and_do_not_fake_materialization",
        }
        interpretation = [
            "V1.34JR converts the first live branch into honest direction.",
            "The branch remains logically first, but the current actionable blocker is name-to-symbol coverage, so no fake broader symbol pool should be claimed from the present local files.",
        ]
        return V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jr_commercial_aerospace_jq_symbol_pool_gap_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
