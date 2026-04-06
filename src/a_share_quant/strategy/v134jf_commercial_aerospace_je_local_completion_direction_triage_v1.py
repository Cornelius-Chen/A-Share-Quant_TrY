from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134je_commercial_aerospace_event_attention_capital_local_completion_audit_v1 import (
    V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Report:
        audit = V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "negative_environment_semantics_to_heat_proxy_stack",
                "direction": "retain_as_frozen_board_local_supervision_stack",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_inside_local_route",
            },
            {
                "component": "current_local_evidence_source",
                "direction": "treat_as_exhausted_do_not_reopen_without_new_attention_or_event_inventory",
            },
            {
                "component": "next_progress_source",
                "direction": "future_only_from_broader_attention_evidence_or_new_retained_symbol_named_heat_source",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jf_commercial_aerospace_je_local_completion_direction_triage_v1",
            "current_local_route_exhausted": audit.summary["current_local_route_exhausted"],
            "capital_true_selection_still_blocked": audit.summary["capital_true_selection_still_blocked"],
            "authoritative_status": "freeze_event_attention_capital_local_route_and_do_not_drift_inside_same_local_inventory",
        }
        interpretation = [
            "V1.34JF converts the local completion audit into direction.",
            "The key move is to stop treating the same local inventory as an open frontier once it has already proven its own stopline.",
        ]
        return V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jf_commercial_aerospace_je_local_completion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
