from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key).lstrip("\ufeff"): value for key, value in row.items()}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [_normalize_row(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


FIELDNAMES = [
    "sample_window_id",
    "anchor_rank",
    "event_date",
    "evidence_extract_id",
    "source_kind",
    "source_title",
    "source_url",
    "anchor_role",
    "anchor_strength",
    "wording_lock_class",
    "is_exact_january_ignition_text",
    "sufficient_for_direction_anchor",
    "sufficient_for_final_training_gate_release",
    "strict_supervisor_judgement",
]

SUMMARY_FIELDNAMES = [
    "sample_window_id",
    "direction_anchor_count",
    "reinforcement_anchor_count",
    "exact_january_ignition_text_locked",
    "direction_anchor_strength_state",
    "reinforcement_state",
    "final_training_admission",
    "strict_supervisor_conclusion",
]


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    extract_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_backfill_evidence_extract_v1.csv"
    )
    extract_rows = _read_csv(extract_path)

    selected_ids = ["ca_extract_002", "ca_extract_003", "ca_extract_013", "ca_extract_015"]
    selected_rows = [row for row in extract_rows if row["evidence_extract_id"] in selected_ids]
    selected_rows.sort(key=lambda row: (row["event_date"], row["evidence_extract_id"]))
    if len(selected_rows) != 4:
        raise ValueError("Policy anchor lock sheet expects 4 specific evidence extracts for window 002 context.")

    role_map = {
        "ca_extract_002": ("national_direction_anchor", "p0", "exact_formal_anchor_but_pre_ignition"),
        "ca_extract_003": ("national_direction_detail", "p0", "exact_formal_detail_but_pre_ignition"),
        "ca_extract_013": ("central_system_reinforcement", "p1", "reinforcement_without_day_of_ignition_text"),
        "ca_extract_015": ("scale_up_reinforcement", "p1", "reinforcement_without_day_of_ignition_text"),
    }
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(selected_rows, start=1):
        anchor_role, anchor_strength, wording_lock_class = role_map[row["evidence_extract_id"]]
        is_exact_january_ignition_text = "true" if row["evidence_extract_id"] == "ca_extract_015_exact_jan_text" else "false"
        rows.append(
            {
                "sample_window_id": "ca_train_window_002",
                "anchor_rank": idx,
                "event_date": row["event_date"],
                "evidence_extract_id": row["evidence_extract_id"],
                "source_kind": row["source_kind"],
                "source_title": row["source_title"],
                "source_url": row["source_url"],
                "anchor_role": anchor_role,
                "anchor_strength": anchor_strength,
                "wording_lock_class": wording_lock_class,
                "is_exact_january_ignition_text": is_exact_january_ignition_text,
                "sufficient_for_direction_anchor": "true",
                "sufficient_for_final_training_gate_release": "false",
                "strict_supervisor_judgement": (
                    "These anchors are strong enough to prove the January move had a real top-down backdrop, "
                    "but none of them replaces an exact day-of-ignition January 8/12 policy text."
                ),
            }
        )

    summary_rows = [
        {
            "sample_window_id": "ca_train_window_002",
            "direction_anchor_count": 2,
            "reinforcement_anchor_count": 2,
            "exact_january_ignition_text_locked": "false",
            "direction_anchor_strength_state": "strong_enough_preconditioning_anchor_present",
            "reinforcement_state": "present_but_not_gate_releasing",
            "final_training_admission": "hold_until_policy_wording_locked",
            "strict_supervisor_conclusion": (
                "Window 002 now has a locked policy stack: a formal national direction anchor plus central-system "
                "and scale-up reinforcements. That is sufficient to explain why January ignition was not random, "
                "but still insufficient to release the final-training gate because the exact January 8/12 ignition text is not locked."
            ),
        }
    ]
    return rows, summary_rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    rows, summary_rows = materialize(repo_root)
    output_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_policy_anchor_lock_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_policy_anchor_lock_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
