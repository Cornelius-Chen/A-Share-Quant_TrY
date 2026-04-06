from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jw_commercial_aerospace_broader_attention_frontier_status_audit_v1 import (
    V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Report:
        audit = V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "broader_symbol_pool_expander",
                "direction": "retain_as_logical_first_branch_but_wait_for_name_to_symbol_coverage_expansion",
            },
            {
                "component": "heat_axis_and_counterpanel_expander",
                "direction": "retain_as_parallel_singleton_reinforcement_branch_only",
            },
            {
                "component": "carrier_follow_search_expander",
                "direction": "retain_as_parallel_known_case_reinforcement_branch_only",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_until_at_least_one_live_branch_turns_promotive",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jx_commercial_aerospace_jw_frontier_status_direction_triage_v1",
            "formalized_same_plane_branch_count": audit.summary["formalized_same_plane_branch_count"],
            "promotive_branch_count": audit.summary["promotive_branch_count"],
            "authoritative_status": "retain_broader_attention_frontier_as_real_but_non_promotive_and_do_not_force_true_selection_from_reinforcement_only_branches",
        }
        interpretation = [
            "V1.34JX converts the consolidated broader-attention frontier status into direction.",
            "The frontier remains alive and structured, but the correct stance is still restraint: no branch should be forced into promotion while all three remain non-promotive for explicit reasons.",
        ]
        return V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jx_commercial_aerospace_jw_frontier_status_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
