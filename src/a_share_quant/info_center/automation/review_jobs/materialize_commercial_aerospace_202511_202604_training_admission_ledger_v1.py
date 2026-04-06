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
    "window_name",
    "current_review_state",
    "training_admission_class",
    "training_role",
    "final_training_admission",
    "supervisor_release_state",
    "strict_supervisor_conclusion",
]

SUMMARY_FIELDNAMES = [
    "window_count",
    "positive_support_sample_ready_count",
    "negative_support_sample_ready_count",
    "final_training_ready_count",
    "positive_sample_ready_count",
    "negative_sample_ready_count",
    "bridge_sample_ready_count",
    "subwindow_learning_only_count",
    "hold_count",
    "under_review_count",
    "strict_supervisor_conclusion",
]


def _classify(row: dict[str, str]) -> dict[str, str]:
    sample_window_id = row["sample_window_id"]
    current_review_state = row["current_review_state"]
    if sample_window_id == "ca_train_window_001":
        return {
            "training_admission_class": "positive_support_sample_ready",
            "training_role": "supply_chain_seed_support_positive",
            "final_training_admission": "positive_support_sample_ready",
            "supervisor_release_state": "released_but_not_final",
        }
    if sample_window_id == "ca_train_window_002":
        return {
            "training_admission_class": "policy_gate_hold",
            "training_role": "primary_positive_archetype",
            "final_training_admission": "hold_until_policy_wording_locked",
            "supervisor_release_state": "hold",
        }
    if sample_window_id == "ca_train_window_003":
        return {
            "training_admission_class": "negative_sample_ready",
            "training_role": "overheat_negative",
            "final_training_admission": "negative_sample_ready",
            "supervisor_release_state": "released",
        }
    if sample_window_id == "ca_train_window_004":
        return {
            "training_admission_class": "negative_support_sample_ready",
            "training_role": "real_anchor_but_not_immediate_tradability",
            "final_training_admission": "negative_support_sample_ready",
            "supervisor_release_state": "released_but_not_final",
        }
    if sample_window_id == "ca_train_window_005":
        return {
            "training_admission_class": "negative_sample_ready",
            "training_role": "logic_valid_board_misaligned_negative",
            "final_training_admission": "negative_sample_ready",
            "supervisor_release_state": "released",
        }
    if sample_window_id == "ca_train_window_006":
        return {
            "training_admission_class": "negative_sample_ready",
            "training_role": "capital_mapping_diffusion_negative",
            "final_training_admission": "negative_sample_ready",
            "supervisor_release_state": "released",
        }
    if sample_window_id == "ca_train_window_007":
        return {
            "training_admission_class": "positive_sample_ready",
            "training_role": "policy_preheat_positive",
            "final_training_admission": "positive_sample_ready_but_not_final_training",
            "supervisor_release_state": "released_but_not_final",
        }
    if sample_window_id == "ca_train_window_008":
        return {
            "training_admission_class": "subwindow_learning_only",
            "training_role": "conference_chain_diffusion_decay",
            "final_training_admission": "subwindow_ready_but_full_window_not_ready",
            "supervisor_release_state": "released_as_subwindow_only",
        }
    if sample_window_id == "ca_train_window_009":
        return {
            "training_admission_class": "bridge_sample_ready",
            "training_role": "cross_narrative_bridge",
            "final_training_admission": "bridge_sample_ready_but_not_final_training",
            "supervisor_release_state": "released_but_not_final",
        }
    if sample_window_id == "ca_train_window_010":
        return {
            "training_admission_class": "negative_sample_ready",
            "training_role": "launch_milestone_negative",
            "final_training_admission": "negative_sample_ready",
            "supervisor_release_state": "released",
        }
    raise KeyError(f"Unhandled sample_window_id: {sample_window_id}, review_state={current_review_state}")


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    review_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_window_reaction_review_sheet_v1.csv"
    )
    rows = _read_csv(review_path)
    if not rows:
        raise FileNotFoundError(review_path)

    output_rows: list[dict[str, Any]] = []
    for row in rows:
        classification = _classify(row)
        output_rows.append(
            {
                "sample_window_id": row["sample_window_id"],
                "window_name": row["window_name"],
                "current_review_state": row["current_review_state"],
                "training_admission_class": classification["training_admission_class"],
                "training_role": classification["training_role"],
                "final_training_admission": classification["final_training_admission"],
                "supervisor_release_state": classification["supervisor_release_state"],
                "strict_supervisor_conclusion": row["strict_supervisor_note"],
            }
        )

    summary_rows = [
        {
            "window_count": len(output_rows),
            "positive_support_sample_ready_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "positive_support_sample_ready"
            ),
            "negative_support_sample_ready_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "negative_support_sample_ready"
            ),
            "final_training_ready_count": sum(
                1 for row in output_rows if row["final_training_admission"] == "final_training_ready"
            ),
            "positive_sample_ready_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "positive_sample_ready"
            ),
            "negative_sample_ready_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "negative_sample_ready"
            ),
            "bridge_sample_ready_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "bridge_sample_ready"
            ),
            "subwindow_learning_only_count": sum(
                1 for row in output_rows if row["training_admission_class"] == "subwindow_learning_only"
            ),
            "hold_count": sum(
                1
                for row in output_rows
                if row["supervisor_release_state"] == "hold"
            ),
            "under_review_count": sum(
                1
                for row in output_rows
                if row["supervisor_release_state"] == "not_released"
            ),
            "strict_supervisor_conclusion": (
                "The commercial-aerospace training band now has released positive-support, negative-support, positive, negative, bridge, and subwindow-only samples, "
                "while the core January ignition archetype remains under a strict policy gate hold."
            ),
        }
    ]
    return output_rows, summary_rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    rows, summary_rows = materialize(repo_root)
    output_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_training_admission_ledger_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_training_admission_ledger_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
