from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134KAAshareInformationCenterStorageLifecyclePolicyV1Report:
    summary: dict[str, Any]
    lifecycle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "lifecycle_rows": self.lifecycle_rows,
            "interpretation": self.interpretation,
        }


class V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_information_center_storage_lifecycle_policy_v1.csv"
        )

    def analyze(self) -> V134KAAshareInformationCenterStorageLifecyclePolicyV1Report:
        lifecycle_rows = [
            {
                "data_class": "raw_intraday_market_data",
                "storage_tier": "hot_then_warm_then_cold",
                "retention_policy": "hot_3m|warm_12m|older_cold_archive",
                "default_exit_action": "rollup_and_archive",
                "rebuildability": "low",
                "why_keep_or_evict": "point_in_time trading reconstruction needs recent detail, but long-term online retention is too expensive",
            },
            {
                "data_class": "raw_daily_market_data",
                "storage_tier": "warm_then_cold",
                "retention_policy": "warm_36m|older_cold_archive",
                "default_exit_action": "archive",
                "rebuildability": "medium",
                "why_keep_or_evict": "daily bars remain analytically useful longer, but do not need premium hot storage indefinitely",
            },
            {
                "data_class": "raw_documents_t0_to_t2",
                "storage_tier": "warm_then_cold",
                "retention_policy": "warm_12m|older_cold_archive_keep_index",
                "default_exit_action": "archive_keep_metadata",
                "rebuildability": "low",
                "why_keep_or_evict": "official and high-authority text should stay retrievable, but not necessarily online in full text forever",
            },
            {
                "data_class": "raw_documents_t3_to_t5_reposts",
                "storage_tier": "hot_then_disposable",
                "retention_policy": "hot_30d_after_extraction_then_evict_or_compact",
                "default_exit_action": "compact_or_evict",
                "rebuildability": "high",
                "why_keep_or_evict": "low-grade repost content is primarily attention evidence and should not accumulate as full-text sludge",
            },
            {
                "data_class": "claim_event_evidence_structures",
                "storage_tier": "frozen_reference",
                "retention_policy": "long_term_keep_versioned",
                "default_exit_action": "never_evict_without_supersession",
                "rebuildability": "low",
                "why_keep_or_evict": "structured evidence is the durable reusable truth layer after raw text is compacted",
            },
            {
                "data_class": "security_master_alias_business_reference",
                "storage_tier": "frozen_reference",
                "retention_policy": "long_term_keep_versioned",
                "default_exit_action": "never_evict_without_version_replacement",
                "rebuildability": "low",
                "why_keep_or_evict": "identity and business-reference history are foundational and should remain queryable forever",
            },
            {
                "data_class": "temporary_feature_views_and_join_surfaces",
                "storage_tier": "disposable",
                "retention_policy": "ttl_7d_or_30d",
                "default_exit_action": "evict",
                "rebuildability": "high",
                "why_keep_or_evict": "derived intermediate tables are classic storage traps and should default to rebuildable TTL assets",
            },
            {
                "data_class": "experiment_candidate_search_outputs",
                "storage_tier": "disposable_then_compacted",
                "retention_policy": "keep_final_audit_only",
                "default_exit_action": "compact_then_evict_intermediates",
                "rebuildability": "high",
                "why_keep_or_evict": "only final audit and handoff artifacts should survive; search exhaust should not become permanent baggage",
            },
            {
                "data_class": "label_registry_feature_registry_state_journals",
                "storage_tier": "frozen_reference",
                "retention_policy": "long_term_keep_versioned",
                "default_exit_action": "append_only_or_version_replace",
                "rebuildability": "low",
                "why_keep_or_evict": "labels, feature definitions, and state journals are the semantic spine of reproducibility",
            },
            {
                "data_class": "shadow_replay_and_execution_journals",
                "storage_tier": "warm_then_cold",
                "retention_policy": "warm_24m|older_cold_archive",
                "default_exit_action": "archive_keep_index",
                "rebuildability": "low",
                "why_keep_or_evict": "shadow journals are expensive but essential for later attribution and dispute resolution",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(lifecycle_rows[0].keys()))
            writer.writeheader()
            writer.writerows(lifecycle_rows)

        summary = {
            "acceptance_posture": "build_v134ka_a_share_information_center_storage_lifecycle_policy_v1",
            "lifecycle_class_count": len(lifecycle_rows),
            "frozen_reference_class_count": sum(row["storage_tier"] == "frozen_reference" for row in lifecycle_rows),
            "disposable_class_count": sum("disposable" in row["storage_tier"] for row in lifecycle_rows),
            "archive_class_count": sum("cold" in row["storage_tier"] for row in lifecycle_rows),
            "lifecycle_policy_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_information_center_storage_lifecycle_policy_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KA makes storage exit a first-class design rule rather than an afterthought.",
            "The information center must be built as a layered lifecycle system: hot recent detail, warm review surfaces, cold archives, frozen truth layers, and disposable rebuildable intermediates.",
        ]
        return V134KAAshareInformationCenterStorageLifecyclePolicyV1Report(
            summary=summary,
            lifecycle_rows=lifecycle_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KAAshareInformationCenterStorageLifecyclePolicyV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ka_a_share_information_center_storage_lifecycle_policy_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
