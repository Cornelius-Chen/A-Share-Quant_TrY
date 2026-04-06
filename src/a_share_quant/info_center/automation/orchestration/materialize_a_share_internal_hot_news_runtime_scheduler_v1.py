from __future__ import annotations

import csv
import importlib
import inspect
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.orchestration.a_share_internal_hot_news_runtime_switch_v1 import (
    HotNewsRuntimeSwitchStoreV1,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


def _to_int(value: str | None, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsRuntimeSchedulerV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    cycle_steps: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsRuntimeSchedulerV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        src_path = str(repo_root / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        self.switch_store = HotNewsRuntimeSwitchStoreV1(repo_root)
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_scheduler_registry_v1.csv"
        )
        self.manifest_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_scheduler_manifest_v1.json"
        )
        self.cls_staging_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "ingest_staging"
            / "a_share_internal_hot_news_cls_telegraph_staging_v1.csv"
        )
        self.sina_staging_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "ingest_staging"
            / "a_share_internal_hot_news_sina_7x24_staging_v1.csv"
        )
        self.snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.status_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_surface_v1.csv"
        )
        self.control_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.retention_queue_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "retention_queue"
            / "a_share_internal_hot_news_retention_queue_v1.csv"
        )
        self.retention_cleanup_log_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_retention_cleanup_log_v1.csv"
        )
        self.retention_cap_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_artifact_retention_cap_registry_v1.csv"
        )

    def _module_names(self) -> list[str]:
        return [
            "a_share_quant.info_center.automation.ingest_jobs.fetch_a_share_internal_hot_news_cls_telegraph_v1",
            "a_share_quant.info_center.automation.ingest_jobs.fetch_a_share_internal_hot_news_sina_7x24_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_sina_theme_probe_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_second_source_probe_comparison_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_review_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_surface_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_fastlane_v1",
            "a_share_quant.info_center.automation.retention_jobs.materialize_a_share_internal_hot_news_retention_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_guidance_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_event_cluster_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_important_promotion_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_signal_enrichment_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_rolling_context_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_scoring_surface_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_program_ingress_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_program_minimal_view_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_split_feeds_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_opportunity_symbol_watch_surface_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watchlist_packet_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watch_summary_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watch_summary_change_signal_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_snapshot_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_snapshot_change_signal_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_change_action_surface_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_change_action_signal_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_status_surface_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_status_change_signal_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_driver_escalation_alert_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_driver_escalation_signal_feed_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_primary_focus_replay_tracker_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_focus_comparison_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_competition_leaderboard_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_review_attention_packet_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_governance_tension_packet_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_rotation_readiness_packet_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_control_packet_v1",
            "a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_control_packet_change_signal_v1",
            "a_share_quant.info_center.automation.retention_jobs.materialize_a_share_internal_hot_news_runtime_artifact_retention_cap_v1",
        ]

    @staticmethod
    def _resolve_materializer_class(module_name: str) -> type[Any]:
        module = importlib.import_module(module_name)
        candidates: list[type[Any]] = []
        for _, value in inspect.getmembers(module, inspect.isclass):
            if value.__module__ != module_name:
                continue
            if hasattr(value, "materialize") and (
                value.__name__.startswith("FetchAShareInternalHotNews")
                or value.__name__.startswith("MaterializeAShareInternalHotNews")
            ):
                candidates.append(value)
        candidates.sort(key=lambda klass: klass.__name__)
        if not candidates:
            raise RuntimeError(f"no materializer class found in {module_name}")
        return candidates[0]

    def _run_scripts(self) -> list[dict[str, Any]]:
        cycle_steps: list[dict[str, Any]] = []
        for module_name in self._module_names():
            started_at = datetime.now(tz=UTC)
            materializer_class = self._resolve_materializer_class(module_name)
            try:
                materialized = materializer_class(self.repo_root).materialize()
                completed_at = datetime.now(tz=UTC)
                cycle_steps.append(
                    {
                        "module_name": module_name,
                        "class_name": materializer_class.__name__,
                        "started_at_utc": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "completed_at_utc": completed_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "step_state": "materialized",
                        "authoritative_output": materialized.summary.get("authoritative_output", ""),
                    }
                )
            except Exception as exc:
                completed_at = datetime.now(tz=UTC)
                fallback_path = None
                if module_name.endswith("fetch_a_share_internal_hot_news_cls_telegraph_v1"):
                    fallback_path = self.cls_staging_path
                elif module_name.endswith("fetch_a_share_internal_hot_news_sina_7x24_v1"):
                    fallback_path = self.sina_staging_path
                if fallback_path is not None and fallback_path.exists():
                    cycle_steps.append(
                        {
                            "module_name": module_name,
                            "class_name": materializer_class.__name__,
                            "started_at_utc": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "completed_at_utc": completed_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "step_state": "fallback_existing_artifact",
                            "authoritative_output": str(fallback_path.relative_to(self.repo_root)),
                            "warning": str(exc),
                        }
                    )
                    continue
                raise
        return cycle_steps

    def _build_registry_row(
        self,
        *,
        started_at_utc: str,
        completed_at_utc: str,
        cycle_state: str,
        cycle_steps: list[dict[str, Any]],
        failure_reason: str = "",
    ) -> dict[str, Any]:
        cls_rows = _read_csv(self.cls_staging_path)
        sina_rows = _read_csv(self.sina_staging_path)
        snapshot_rows = _read_csv(self.snapshot_path)
        status_rows = _read_csv(self.status_path)
        control_rows = _read_csv(self.control_packet_path)
        retention_queue_rows = [
            row for row in _read_csv(self.retention_queue_path) if row.get("telegraph_id")
        ]
        retention_cleanup_rows = [
            row for row in _read_csv(self.retention_cleanup_log_path) if row.get("telegraph_id")
        ]
        retention_cap_rows = _read_csv(self.retention_cap_registry_path)

        snapshot = snapshot_rows[0] if snapshot_rows else {}
        status = status_rows[0] if status_rows else {}
        control = control_rows[0] if control_rows else {}
        retention_cap = retention_cap_rows[0] if retention_cap_rows else {}

        return {
            "runtime_id": "internal_hot_news_runtime_scheduler",
            "runtime_state": cycle_state,
            "execution_mode": "single_cycle_runner",
            "last_cycle_started_at_utc": started_at_utc,
            "last_cycle_completed_at_utc": completed_at_utc,
            "cls_fetch_row_count": str(len(cls_rows)),
            "sina_fetch_row_count": str(len(sina_rows)),
            "executed_step_count": str(len(cycle_steps)),
            "cycle_failure_reason": failure_reason,
            "program_health_state": status.get("program_health_state", "unknown"),
            "freshness_state": status.get("freshness_state", "unknown"),
            "heartbeat_timeout_state": status.get("heartbeat_timeout_state", "unknown"),
            "program_driver_action_mode": status.get("program_driver_action_mode", "unknown"),
            "top_opportunity_theme": snapshot.get("top_opportunity_primary_theme_slug", "none"),
            "top_watch_symbol": snapshot.get("top_watch_symbol", ""),
            "focus_rotation_readiness_state": control.get("focus_rotation_readiness_state", "unknown"),
            "challenger_review_state": control.get("challenger_review_state", "unknown"),
            "retention_active_queue_count": str(len(retention_queue_rows)),
            "retention_expired_cleanup_count": str(len(retention_cleanup_rows)),
            "retention_cap_pruned_file_count": retention_cap.get("pruned_file_count", "0"),
            "retention_cap_removed_row_count": retention_cap.get("removed_row_count", "0"),
            "next_suggested_poll_interval_seconds": "300",
            "notes": "single-cycle runtime scheduler ready for external cron/task-scheduler triggering",
        }

    def materialize(self) -> MaterializedAShareInternalHotNewsRuntimeSchedulerV1:
        started_at = datetime.now(tz=UTC)
        cycle_steps: list[dict[str, Any]] = []
        failure_reason = ""
        switch_state = self.switch_store.read()
        cycle_state = "cycle_completed"
        if switch_state.enabled:
            try:
                cycle_steps = self._run_scripts()
            except Exception as exc:
                cycle_state = "cycle_failed"
                failure_reason = str(exc)
        else:
            cycle_state = "runtime_disabled_skip"
        completed_at = datetime.now(tz=UTC)

        row = self._build_registry_row(
            started_at_utc=started_at.strftime("%Y-%m-%d %H:%M:%S"),
            completed_at_utc=completed_at.strftime("%Y-%m-%d %H:%M:%S"),
            cycle_state=cycle_state,
            cycle_steps=cycle_steps,
            failure_reason=failure_reason,
        )
        _write_csv(self.registry_path, [row])

        manifest = {
            "summary": {
                "runtime_state": row["runtime_state"],
                "executed_step_count": int(row["executed_step_count"]),
                "cls_fetch_row_count": int(row["cls_fetch_row_count"]),
                "sina_fetch_row_count": int(row["sina_fetch_row_count"]),
                "top_opportunity_theme": row["top_opportunity_theme"],
                "top_watch_symbol": row["top_watch_symbol"],
                "program_health_state": row["program_health_state"],
                "freshness_state": row["freshness_state"],
                "focus_rotation_readiness_state": row["focus_rotation_readiness_state"],
                "retention_active_queue_count": int(row["retention_active_queue_count"]),
                "retention_expired_cleanup_count": int(row["retention_expired_cleanup_count"]),
                "retention_cap_pruned_file_count": int(row["retention_cap_pruned_file_count"]),
                "retention_cap_removed_row_count": int(row["retention_cap_removed_row_count"]),
            },
            "cycle_steps": cycle_steps,
        }
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        summary = {
            "runtime_state": row["runtime_state"],
            "executed_step_count": int(row["executed_step_count"]),
            "cls_fetch_row_count": _to_int(row["cls_fetch_row_count"]),
            "sina_fetch_row_count": _to_int(row["sina_fetch_row_count"]),
            "runtime_enabled": switch_state.enabled,
            "top_opportunity_theme": row["top_opportunity_theme"],
            "top_watch_symbol": row["top_watch_symbol"],
            "program_health_state": row["program_health_state"],
            "freshness_state": row["freshness_state"],
            "focus_rotation_readiness_state": row["focus_rotation_readiness_state"],
            "retention_active_queue_count": _to_int(row["retention_active_queue_count"]),
            "retention_expired_cleanup_count": _to_int(row["retention_expired_cleanup_count"]),
            "retention_cap_pruned_file_count": _to_int(row["retention_cap_pruned_file_count"]),
            "retention_cap_removed_row_count": _to_int(row["retention_cap_removed_row_count"]),
            "authoritative_output": "a_share_internal_hot_news_runtime_scheduler_materialized",
        }
        if cycle_state != "cycle_completed":
            if cycle_state == "runtime_disabled_skip":
                return MaterializedAShareInternalHotNewsRuntimeSchedulerV1(
                    summary=summary,
                    rows=[row],
                    cycle_steps=cycle_steps,
                )
            raise RuntimeError(failure_reason or "runtime scheduler cycle failed")
        return MaterializedAShareInternalHotNewsRuntimeSchedulerV1(
            summary=summary,
            rows=[row],
            cycle_steps=cycle_steps,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareInternalHotNewsRuntimeSchedulerV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
