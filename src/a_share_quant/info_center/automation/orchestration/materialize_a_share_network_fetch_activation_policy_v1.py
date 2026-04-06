from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class MaterializedAShareNetworkFetchActivationPolicyV1:
    summary: dict[str, Any]
    adapter_policy_rows: list[dict[str, Any]]
    retry_policy_rows: list[dict[str, Any]]
    orchestration_binding_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareNetworkFetchActivationPolicyV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.adapter_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_adapter_registry_v1.csv"
        )
        self.host_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_host_registry_v1.csv"
        )
        self.orchestration_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_orchestration_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.adapter_policy_path = self.output_dir / "a_share_network_fetch_activation_policy_v1.csv"
        self.retry_policy_path = self.output_dir / "a_share_network_fetch_retry_policy_v1.csv"
        self.orchestration_binding_path = (
            self.output_dir / "a_share_network_fetch_orchestration_binding_v1.csv"
        )
        self.residual_path = self.output_dir / "a_share_network_fetch_activation_policy_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_network_fetch_activation_policy_manifest_v1.json"

    def materialize(self) -> MaterializedAShareNetworkFetchActivationPolicyV1:
        adapter_rows = _read_csv(self.adapter_registry_path)
        host_rows = _read_csv(self.host_registry_path)
        flow_rows = _read_csv(self.orchestration_registry_path)
        flow_ids = {row["flow_id"] for row in flow_rows}
        default_flow_id = "daily_bootstrap_cycle"
        if default_flow_id not in flow_ids:
            raise ValueError("daily_bootstrap_cycle orchestration flow is required")

        adapter_policy_rows = [
            {
                "adapter_id": "network_html_article_fetch",
                "activation_posture": "selective_after_license_review",
                "flow_id": default_flow_id,
                "retry_policy_id": "html_article_standard_retry",
                "review_queue_id": "low_confidence_event_queue",
                "license_gate": "manual_allowlist_or_known_terms_required",
                "activation_state": "policy_bound_not_activated",
            },
            {
                "adapter_id": "network_social_column_fetch",
                "activation_posture": "review_only_deferred",
                "flow_id": default_flow_id,
                "retry_policy_id": "social_source_conservative_retry",
                "review_queue_id": "attention_soft_candidate_queue",
                "license_gate": "manual_allowlist_required",
                "activation_state": "policy_bound_not_activated",
            },
            {
                "adapter_id": "network_official_source_fetch",
                "activation_posture": "reserved_for_future_primary_sources",
                "flow_id": default_flow_id,
                "retry_policy_id": "official_source_strict_retry",
                "review_queue_id": "contradiction_queue",
                "license_gate": "known_terms_or_contract_required",
                "activation_state": "policy_bound_not_activated",
            },
        ]
        retry_policy_rows = [
            {
                "retry_policy_id": "html_article_standard_retry",
                "backoff_profile": "exponential_short",
                "max_attempts": "3",
                "cooldown_scope": "per_host_daily",
            },
            {
                "retry_policy_id": "social_source_conservative_retry",
                "backoff_profile": "linear_guarded",
                "max_attempts": "2",
                "cooldown_scope": "per_host_manual_review_window",
            },
            {
                "retry_policy_id": "official_source_strict_retry",
                "backoff_profile": "exponential_medium",
                "max_attempts": "4",
                "cooldown_scope": "per_host_daily",
            },
        ]

        orchestration_binding_rows: list[dict[str, Any]] = []
        selective_candidate_host_count = 0
        ready_now_host_count = 0
        deferred_host_count = 0
        for row in host_rows:
            adapter_family = row["adapter_family"]
            if adapter_family in {"html_article_fetch", "html_article_fetch_with_review_bias"}:
                adapter_id = "network_html_article_fetch"
                review_queue_id = "low_confidence_event_queue"
                activation_gate = "license_review_required"
                host_activation_state = "selective_candidate_blocked_by_license"
                selective_candidate_host_count += 1
            elif adapter_family == "social_column_fetch_with_noise_guard":
                adapter_id = "network_social_column_fetch"
                review_queue_id = "attention_soft_candidate_queue"
                activation_gate = "manual_review_only"
                host_activation_state = "deferred_review_only"
                deferred_host_count += 1
            else:
                adapter_id = "network_official_source_fetch"
                review_queue_id = "contradiction_queue"
                activation_gate = "future_primary_source_only"
                host_activation_state = "reserved_for_future_primary_source"
                deferred_host_count += 1
            if host_activation_state == "ready_now":
                ready_now_host_count += 1
            orchestration_binding_rows.append(
                {
                    "source_id": row["source_id"],
                    "host": row["host"],
                    "adapter_id": adapter_id,
                    "flow_id": default_flow_id,
                    "activation_gate": activation_gate,
                    "review_queue_id": review_queue_id,
                    "host_activation_state": host_activation_state,
                }
            )

        residual_rows = [
            {
                "residual_class": "license_review_unresolved",
                "residual_reason": "all currently catalogued hosts still require manual license resolution before selective activation",
            },
            {
                "residual_class": "runtime_scheduler_not_activated",
                "residual_reason": "adapter policies are bound to orchestration flows but not yet attached to a live scheduler runtime",
            },
            {
                "residual_class": "official_source_adapter_unpopulated",
                "residual_reason": "official-source adapter remains reserved because no retained T0/T1 host bindings exist yet",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.adapter_policy_path, adapter_policy_rows)
        _write(self.retry_policy_path, retry_policy_rows)
        _write(self.orchestration_binding_path, orchestration_binding_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "adapter_policy_count": len(adapter_policy_rows),
            "retry_policy_count": len(retry_policy_rows),
            "host_binding_count": len(orchestration_binding_rows),
            "selective_candidate_host_count": selective_candidate_host_count,
            "ready_now_host_count": ready_now_host_count,
            "deferred_host_count": deferred_host_count,
            "adapter_policy_path": str(self.adapter_policy_path.relative_to(self.repo_root)),
            "retry_policy_path": str(self.retry_policy_path.relative_to(self.repo_root)),
            "binding_path": str(self.orchestration_binding_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareNetworkFetchActivationPolicyV1(
            summary=summary,
            adapter_policy_rows=adapter_policy_rows,
            retry_policy_rows=retry_policy_rows,
            orchestration_binding_rows=orchestration_binding_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareNetworkFetchActivationPolicyV1(repo_root).materialize()
    print(result.summary["adapter_policy_path"])


if __name__ == "__main__":
    main()
