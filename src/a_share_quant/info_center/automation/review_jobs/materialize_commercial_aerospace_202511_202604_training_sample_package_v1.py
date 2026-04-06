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
    "training_admission_class",
    "training_role",
    "final_training_admission",
    "package_tier",
    "package_usage_mode",
    "include_in_primary_fit",
    "include_in_auxiliary_fit",
    "include_in_reference_set",
    "include_in_locked_holdout",
    "sample_weight",
    "strict_supervisor_conclusion",
]

SUMMARY_FIELDNAMES = [
    "window_count",
    "primary_fit_count",
    "auxiliary_fit_count",
    "reference_only_count",
    "locked_holdout_count",
    "strict_supervisor_conclusion",
]


def _classify(row: dict[str, str]) -> dict[str, Any]:
    sample_window_id = row["sample_window_id"]
    training_class = row["training_admission_class"]

    if sample_window_id == "ca_train_window_002":
        return {
            "package_tier": "locked_holdout",
            "package_usage_mode": "policy_gate_locked_primary_positive_archetype",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 0,
            "include_in_reference_set": 0,
            "include_in_locked_holdout": 1,
            "sample_weight": 0.0,
        }
    if sample_window_id == "ca_train_window_008":
        return {
            "package_tier": "reference_only",
            "package_usage_mode": "subwindow_learning_reference_only",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 0,
            "include_in_reference_set": 1,
            "include_in_locked_holdout": 0,
            "sample_weight": 0.0,
        }
    if training_class == "positive_support_sample_ready":
        return {
            "package_tier": "auxiliary_fit",
            "package_usage_mode": "positive_support_only",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 1,
            "include_in_reference_set": 0,
            "include_in_locked_holdout": 0,
            "sample_weight": 0.55,
        }
    if training_class == "negative_support_sample_ready":
        return {
            "package_tier": "auxiliary_fit",
            "package_usage_mode": "negative_support_only",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 1,
            "include_in_reference_set": 0,
            "include_in_locked_holdout": 0,
            "sample_weight": 0.6,
        }
    if training_class == "positive_sample_ready":
        return {
            "package_tier": "reference_only",
            "package_usage_mode": "positive_context_reference_until_primary_archetype_unlocks",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 0,
            "include_in_reference_set": 1,
            "include_in_locked_holdout": 0,
            "sample_weight": 0.0,
        }
    if training_class == "bridge_sample_ready":
        return {
            "package_tier": "auxiliary_fit",
            "package_usage_mode": "bridge_specific_auxiliary_fit",
            "include_in_primary_fit": 0,
            "include_in_auxiliary_fit": 1,
            "include_in_reference_set": 0,
            "include_in_locked_holdout": 0,
            "sample_weight": 0.5,
        }
    if training_class == "negative_sample_ready":
        if sample_window_id == "ca_train_window_006":
            return {
                "package_tier": "auxiliary_fit",
                "package_usage_mode": "capital_mapping_negative_auxiliary_fit",
                "include_in_primary_fit": 0,
                "include_in_auxiliary_fit": 1,
                "include_in_reference_set": 0,
                "include_in_locked_holdout": 0,
                "sample_weight": 0.65,
            }
        if sample_window_id == "ca_train_window_010":
            return {
                "package_tier": "reference_only",
                "package_usage_mode": "launch_milestone_negative_reference_only",
                "include_in_primary_fit": 0,
                "include_in_auxiliary_fit": 0,
                "include_in_reference_set": 1,
                "include_in_locked_holdout": 0,
                "sample_weight": 0.0,
            }
        return {
            "package_tier": "primary_fit",
            "package_usage_mode": "core_negative_fit",
            "include_in_primary_fit": 1,
            "include_in_auxiliary_fit": 0,
            "include_in_reference_set": 0,
            "include_in_locked_holdout": 0,
            "sample_weight": 1.0,
        }
    raise KeyError(f"Unhandled package class for {sample_window_id}: {training_class}")


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ledger_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_admission_ledger_v1.csv"
    )
    rows = _read_csv(ledger_path)
    if not rows:
        raise FileNotFoundError(ledger_path)

    output_rows: list[dict[str, Any]] = []
    for row in rows:
        pkg = _classify(row)
        output_rows.append(
            {
                "sample_window_id": row["sample_window_id"],
                "window_name": row["window_name"],
                "training_admission_class": row["training_admission_class"],
                "training_role": row["training_role"],
                "final_training_admission": row["final_training_admission"],
                "package_tier": pkg["package_tier"],
                "package_usage_mode": pkg["package_usage_mode"],
                "include_in_primary_fit": pkg["include_in_primary_fit"],
                "include_in_auxiliary_fit": pkg["include_in_auxiliary_fit"],
                "include_in_reference_set": pkg["include_in_reference_set"],
                "include_in_locked_holdout": pkg["include_in_locked_holdout"],
                "sample_weight": pkg["sample_weight"],
                "strict_supervisor_conclusion": row["strict_supervisor_conclusion"],
            }
        )

    summary_rows = [
        {
            "window_count": len(output_rows),
            "primary_fit_count": sum(1 for row in output_rows if row["package_tier"] == "primary_fit"),
            "auxiliary_fit_count": sum(1 for row in output_rows if row["package_tier"] == "auxiliary_fit"),
            "reference_only_count": sum(1 for row in output_rows if row["package_tier"] == "reference_only"),
            "locked_holdout_count": sum(1 for row in output_rows if row["package_tier"] == "locked_holdout"),
            "strict_supervisor_conclusion": (
                "This package intentionally keeps window 002 locked out of fitting, keeps 007/008/010 as reference only, "
                "uses 001/004/006/009 as auxiliary training context, and promotes only the cleanest released negative windows "
                "into primary fitting."
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
        / "commercial_aerospace_202511_202604_training_sample_package_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_training_sample_package_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
