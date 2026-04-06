from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kl_a_share_attention_foundation_audit_v1 import (
    V134KLAShareAttentionFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KMAShareKLAttentionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KMAShareKLAttentionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KMAShareKLAttentionDirectionTriageV1Report:
        audit = V134KLAShareAttentionFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "attention_component": "attention_registry",
                "direction": "retain_as_bootstrap_attention_center_surface_and_expand_beyond_commercial_aerospace_only_after_more_hard_cases_exist",
            },
            {
                "attention_component": "hard_attention_roles",
                "direction": "keep_singleton_hard_case_without_forcing_a_second_anchor_or_decoy",
            },
            {
                "attention_component": "soft_attention_candidates",
                "direction": "consume_as_backlog_for_future_review_and_quality_linking_not_as_hard_trade_permission",
            },
            {
                "attention_component": "next_frontier",
                "direction": "move_into_labels_layer_using_attention_registry_as_semantic_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134km_a_share_kl_attention_direction_triage_v1",
            "attention_registry_count": audit.summary["attention_registry_count"],
            "hard_attention_role_count": audit.summary["hard_attention_role_count"],
            "authoritative_status": "attention_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_label_registry_population",
        }
        interpretation = [
            "V1.34KM converts the attention audit into direction.",
            "The correct next move is to let labels consume the attention surface, not to overpromote soft candidates into hard attention truths prematurely.",
        ]
        return V134KMAShareKLAttentionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KMAShareKLAttentionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KMAShareKLAttentionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134km_a_share_kl_attention_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
