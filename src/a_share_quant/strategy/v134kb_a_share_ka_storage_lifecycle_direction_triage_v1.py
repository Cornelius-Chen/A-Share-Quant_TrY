from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ka_a_share_information_center_storage_lifecycle_policy_v1 import (
    V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer,
)


@dataclass(slots=True)
class V134KBAShareKAStorageLifecycleDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KBAShareKAStorageLifecycleDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KBAShareKAStorageLifecycleDirectionTriageV1Report:
        audit = V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "priority_band": "p0",
                "direction": "treat_security_master_alias_business_reference_and_structured_claim_event_layers_as_frozen_reference",
            },
            {
                "priority_band": "p0",
                "direction": "default_temporary_feature_views_and_candidate_search_outputs_to_ttl_backed_disposable_assets",
            },
            {
                "priority_band": "p1",
                "direction": "compact_low_tier_raw_documents_into_claim_event_attention_summaries_before_storage_bloat_accumulates",
            },
            {
                "priority_band": "p1",
                "direction": "keep_recent_intraday_detail_hot_only_for_shadow_and_research_windows_then_roll_up_or_archive",
            },
            {
                "priority_band": "p2",
                "direction": "keep_shadow_and_execution_journals_longer_than_raw_market_noise_because_replay_and_dispute_resolution_depend_on_them",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kb_a_share_ka_storage_lifecycle_direction_triage_v1",
            "lifecycle_class_count": audit.summary["lifecycle_class_count"],
            "disposable_class_count": audit.summary["disposable_class_count"],
            "authoritative_status": "treat_storage_exit_as_first_class_and_keep_only_truth_layers_long_lived_while_defaulting_intermediates_to_ttl_or_archive",
        }
        interpretation = [
            "V1.34KB converts the lifecycle policy into operating direction.",
            "The key discipline is asymmetry: truth layers stay, replay journals stay long enough, but intermediates and low-grade raw text should be aggressively compacted or evicted.",
        ]
        return V134KBAShareKAStorageLifecycleDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KBAShareKAStorageLifecycleDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KBAShareKAStorageLifecycleDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kb_a_share_ka_storage_lifecycle_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
