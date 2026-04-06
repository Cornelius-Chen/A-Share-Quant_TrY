from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.plan_summary_path = (
            derived / "a_share_internal_hot_news_accepted_rotation_primary_consumer_promotion_plan_summary_v1.csv"
        )
        self.accepted_packet_path = derived / "a_share_internal_hot_news_accepted_rotation_candidate_packet_v1.csv"
        self.challenger_plan_summary_path = (
            derived / "a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_summary_v1.csv"
        )
        self.challenger_packet_path = (
            derived / "a_share_internal_hot_news_challenger_rotation_candidate_packet_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1:
        challenger_plan_rows = _read_csv(self.challenger_plan_summary_path)
        challenger_packet_rows = _read_csv(self.challenger_packet_path)

        if challenger_plan_rows and challenger_packet_rows:
            plan_summary = challenger_plan_rows[0]
            accepted_packet = challenger_packet_rows[0]
            accepted_theme = accepted_packet["challenger_top_opportunity_theme"]
            accepted_symbol = accepted_packet["challenger_top_watch_symbol"]
            accepted_source_family = accepted_packet["challenger_source_family"]
            accepted_source_row_id = accepted_packet["challenger_source_row_id"]
            acceptance_scope = "primary_consumer_chain"
            promotion_state = plan_summary["rotation_review_state"]
        else:
            plan_summary = _read_csv(self.plan_summary_path)[0]
            accepted_packet = _read_csv(self.accepted_packet_path)[0]
            accepted_theme = accepted_packet["accepted_top_opportunity_theme"]
            accepted_symbol = accepted_packet["accepted_top_watch_symbol"]
            accepted_source_family = accepted_packet["accepted_source_family"]
            accepted_source_row_id = accepted_packet["accepted_source_row_id"]
            acceptance_scope = "primary_snapshot_and_control_packet_only"
            promotion_state = plan_summary["promotion_gate_state"]

        row = {
            "acceptance_id": "internal_hot_news_primary_consumer_rotation_acceptance_latest",
            "acceptance_state": "accepted",
            "accepted_top_opportunity_theme": accepted_theme,
            "accepted_top_watch_symbol": accepted_symbol,
            "accepted_source_family": accepted_source_family,
            "accepted_source_row_id": accepted_source_row_id,
            "promotion_gate_state_at_acceptance": promotion_state,
            "acceptance_scope": acceptance_scope,
            "delivery_state": "rotation_acceptance_registry_ready",
        }

        _write_csv(self.output_path, [row])

        summary = {
            "acceptance_row_count": 1,
            "acceptance_state": row["acceptance_state"],
            "accepted_top_opportunity_theme": row["accepted_top_opportunity_theme"],
            "accepted_top_watch_symbol": row["accepted_top_watch_symbol"],
            "authoritative_output": "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_materialized",
        }
        return MaterializedAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
