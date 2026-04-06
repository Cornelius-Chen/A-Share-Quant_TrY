from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ni_a_share_network_queue_priority_audit_v1 import (
    V134NIAShareNetworkQueuePriorityAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NJAShareNINetworkQueueDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NJAShareNINetworkQueueDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NJAShareNINetworkQueueDirectionTriageV1Report:
        report = V134NIAShareNetworkQueuePriorityAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "allowlist_batch_one_count": report.summary["allowlist_batch_one_count"],
            "allowlist_batch_two_count": report.summary["allowlist_batch_two_count"],
            "allowlist_deferred_count": report.summary["allowlist_deferred_count"],
            "authoritative_status": "network_queue_processing_should_follow_priority_batches_not_flat_activation",
        }
        triage_rows = [
            {
                "component": "allowlist_batch_one",
                "direction": "review_batch_one_t2_hosts_first_before_any_batch_two_or_runtime_promotion",
            },
            {
                "component": "allowlist_batch_two",
                "direction": "hold_batch_two_secondary_hosts_until_batch_one_license_review_outcomes_exist",
            },
            {
                "component": "allowlist_deferred",
                "direction": "keep_unclear_hosts_deferred_and_out_of_activation_promotion",
            },
            {
                "component": "runtime_html_article_fetch",
                "direction": "treat_html_article_fetch_as_only_first_runtime_candidate_after_batch_one_review",
            },
            {
                "component": "runtime_other_adapters",
                "direction": "keep_social_column_and_official_source_adapters_nonoperative_for_now",
            },
        ]
        interpretation = [
            "The next real source-side work is queue processing in priority order, not more gate rewording.",
            "This still does not open network fetch automatically; it only creates a disciplined first-pass review order.",
        ]
        return V134NJAShareNINetworkQueueDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NJAShareNINetworkQueueDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NJAShareNINetworkQueueDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nj_a_share_ni_network_queue_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
