from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hw_commercial_aerospace_event_attention_supervision_registry_v1 import (
    V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer,
)


@dataclass(slots=True)
class V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Report:
        registry = V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "supervision_label": "event_trigger_validity",
                "direction": "retain_as_first_event_layer_and_keep_validity_categories_conservative",
            },
            {
                "supervision_label": "attention_anchor",
                "direction": "retain_as_role_label_not_as_board_restart_evidence",
            },
            {
                "supervision_label": "attention_decoy",
                "direction": "retain_as_role_label_and_expand_only_after_more_hard_cases_exist",
            },
            {
                "supervision_label": "capital_true_selection",
                "direction": "keep_deferred_until_anchor_and_decoy_labels_exist_beyond_single_hard_case",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134hx_commercial_aerospace_hw_event_attention_direction_triage_v1",
            "registry_row_count": registry.summary["registry_row_count"],
            "authoritative_status": "retain_first_event_attention_registry_as_conservative_supervision_only_seed_layer_and_do_not_pretend_capital_selection_is_ready",
        }
        interpretation = [
            "V1.34HX converts the first event-attention registry into direction.",
            "The event layer is open, but it remains intentionally conservative: anchor and decoy roles can be learned before true selection is promoted.",
        ]
        return V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hx_commercial_aerospace_hw_event_attention_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
