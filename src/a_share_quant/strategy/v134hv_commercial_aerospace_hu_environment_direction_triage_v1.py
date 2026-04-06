from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hu_commercial_aerospace_negative_environment_semantics_registry_v1 import (
    V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer,
)


@dataclass(slots=True)
class V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Report:
        registry = V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "semantic_name": "attention_distorted",
                "direction": "retain_as_primary_negative_environment_semantic_and_do_not_confuse_symbol_heat_with_board_restart",
            },
            {
                "semantic_name": "capital_misaligned_with_board",
                "direction": "retain_as_primary_negative_environment_semantic_and_use_before_true_selection_training",
            },
            {
                "semantic_name": "board_fragile_divergence",
                "direction": "retain_as_higher_level_veto_semantic_above_add_reentry",
            },
            {
                "semantic_name": "external_policy_news_context",
                "direction": "keep_deferred_to_event_attention_layer_not_current_registry",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134hv_commercial_aerospace_hu_environment_direction_triage_v1",
            "semantic_count": registry.summary["semantic_count"],
            "authoritative_status": "retain_negative_environment_semantics_as_next_main_supervision_frontier_and_keep_them_board_local_until_event_attention_labels_exist",
        }
        interpretation = [
            "V1.34HV converts the first environment-level registry into direction.",
            "The board-local semantics are strong enough to promote, but they are not yet the full environment truth; policy/news context still belongs to the next layer rather than being silently backfilled now.",
        ]
        return V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hv_commercial_aerospace_hu_environment_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
