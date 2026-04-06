from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _sort_key(value: str) -> tuple[int, datetime | None]:
    if not value:
        return (1, None)
    return (0, _parse_ts(value))


@dataclass(slots=True)
class MaterializedASharePTIFoundationV1:
    summary: dict[str, Any]
    event_ledger_rows: list[dict[str, Any]]
    time_slice_rows: list[dict[str, Any]]
    state_transition_rows: list[dict[str, Any]]
    transition_backlog_rows: list[dict[str, Any]]


class MaterializeASharePTIFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.event_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "event_registry" / "a_share_event_registry_v1.csv"
        )
        self.event_quality_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_event_quality_registry_v1.csv"
        )
        self.label_assignment_path = (
            repo_root / "data" / "reference" / "info_center" / "label_registry" / "a_share_label_assignment_v1.csv"
        )
        self.attention_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "attention_registry" / "a_share_attention_registry_v1.csv"
        )
        self.feature_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "feature_registry" / "a_share_feature_registry_v1.csv"
        )
        self.event_ledger_dir = repo_root / "data" / "reference" / "info_center" / "event_registry"
        self.time_slice_dir = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.state_transition_dir = repo_root / "data" / "reference" / "info_center" / "state_transition_journal"
        self.event_ledger_path = self.event_ledger_dir / "a_share_pti_event_ledger_v1.csv"
        self.time_slice_path = self.time_slice_dir / "a_share_time_slice_view_v1.csv"
        self.state_transition_path = self.state_transition_dir / "a_share_state_transition_journal_v1.csv"
        self.transition_backlog_path = self.state_transition_dir / "a_share_state_transition_backlog_v1.csv"
        self.manifest_path = self.state_transition_dir / "a_share_pti_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedASharePTIFoundationV1:
        event_rows = self._read_csv(self.event_registry_path)
        event_quality_rows = self._read_csv(self.event_quality_path)
        label_rows = self._read_csv(self.label_assignment_path)
        attention_rows = self._read_csv(self.attention_registry_path)
        feature_registry_rows = self._read_csv(self.feature_registry_path)

        event_quality_map = {row["event_id"]: row for row in event_quality_rows}
        label_count_by_event: dict[str, int] = {}
        for row in label_rows:
            if row["target_type"] == "event":
                label_count_by_event[row["target_id"]] = label_count_by_event.get(row["target_id"], 0) + 1

        event_ledger_rows: list[dict[str, Any]] = []
        for row in event_rows:
            visible_ts = row["system_visible_ts"] or row["public_ts"] or row["event_occurred_ts"]
            quality_row = event_quality_map.get(row["event_id"], {})
            event_ledger_rows.append(
                {
                    "event_id": row["event_id"],
                    "decision_ts": visible_ts,
                    "public_ts": row["public_ts"],
                    "system_visible_ts": row["system_visible_ts"],
                    "timezone": row["timezone"],
                    "visibility_status": "visible_timestamped" if visible_ts else "visibility_backlog",
                    "timestamp_resolution_status": row["timestamp_resolution_status"],
                    "timestamp_quality_band": quality_row.get("timestamp_quality_band", ""),
                    "bootstrap_evidence_gate": quality_row.get("bootstrap_evidence_gate", ""),
                    "event_label_count": label_count_by_event.get(row["event_id"], 0),
                }
            )

        sorted_events = sorted(event_ledger_rows, key=lambda row: _sort_key(row["decision_ts"]))
        time_slice_rows: list[dict[str, Any]] = []
        cumulative_visible = 0
        cumulative_gate_true = 0
        distinct_ts = []
        for row in sorted_events:
            if row["decision_ts"] and row["decision_ts"] not in distinct_ts:
                distinct_ts.append(row["decision_ts"])
        for ts in distinct_ts:
            rows_at_ts = [row for row in sorted_events if row["decision_ts"] == ts]
            cumulative_visible += len(rows_at_ts)
            cumulative_gate_true += sum(1 for row in rows_at_ts if str(row["bootstrap_evidence_gate"]) == "True")
            time_slice_rows.append(
                {
                    "slice_id": f"slice_{ts.replace('-', '').replace(':', '').replace(' ', '_')}",
                    "decision_ts": ts,
                    "visible_event_count": cumulative_visible,
                    "visible_high_conf_event_count": cumulative_gate_true,
                    "available_feature_definition_count": sum(
                        row["registry_status"] == "defined" for row in feature_registry_rows
                    ),
                }
            )

        state_transition_rows: list[dict[str, Any]] = []
        for row in sorted_events:
            state_transition_rows.append(
                {
                    "transition_id": f"{row['event_id']}::visible",
                    "target_type": "event",
                    "target_id": row["event_id"],
                    "decision_ts": row["decision_ts"],
                    "from_state": "unseen",
                    "to_state": "visible_event" if row["decision_ts"] else "visibility_backlog_event",
                    "transition_class": "event_visibility" if row["decision_ts"] else "event_visibility_backlog",
                    "quality_gate": row["bootstrap_evidence_gate"],
                }
            )
        for row in attention_rows:
            state_transition_rows.append(
                {
                    "transition_id": f"{row['symbol']}::attention_role",
                    "target_type": "symbol_attention",
                    "target_id": row["symbol"],
                    "decision_ts": "",
                    "from_state": "unclassified",
                    "to_state": "hard_attention_case" if row["candidate_status"] == "hard_retained" else "soft_attention_candidate",
                    "transition_class": "attention_bootstrap",
                    "quality_gate": row["quality_guardrail"],
                }
            )

        transition_backlog_rows = [
            {
                "transition_family": "board_state_transitions",
                "backlog_reason": "requires board regime and later serving integration",
            },
            {
                "transition_family": "reentry_unlock_transitions",
                "backlog_reason": "requires later integration with frozen research state machines",
            },
            {
                "transition_family": "execution_transitions",
                "backlog_reason": "requires replay and serving layers before lawful materialization",
            },
        ]

        for path in (self.event_ledger_dir, self.time_slice_dir, self.state_transition_dir):
            path.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.event_ledger_path, event_ledger_rows)
        _write(self.time_slice_path, time_slice_rows)
        _write(self.state_transition_path, state_transition_rows)
        _write(self.transition_backlog_path, transition_backlog_rows)

        summary = {
            "event_ledger_count": len(event_ledger_rows),
            "time_slice_count": len(time_slice_rows),
            "state_transition_count": len(state_transition_rows),
            "transition_backlog_count": len(transition_backlog_rows),
            "event_ledger_path": str(self.event_ledger_path.relative_to(self.repo_root)),
            "time_slice_path": str(self.time_slice_path.relative_to(self.repo_root)),
            "state_transition_path": str(self.state_transition_path.relative_to(self.repo_root)),
            "transition_backlog_path": str(self.transition_backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedASharePTIFoundationV1(
            summary=summary,
            event_ledger_rows=event_ledger_rows,
            time_slice_rows=time_slice_rows,
            state_transition_rows=state_transition_rows,
            transition_backlog_rows=transition_backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeASharePTIFoundationV1(repo_root).materialize()
    print(result.summary["event_ledger_path"])


if __name__ == "__main__":
    main()
