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


EXPORT_FIELDNAMES = [
    "task_id",
    "task_name",
    "sample_window_id",
    "window_name",
    "training_role",
    "package_tier",
    "package_usage_mode",
    "task_usage_tier",
    "allow_in_task_fit",
    "allow_as_task_reference",
    "allow_as_task_holdout",
    "task_sample_weight",
    "strict_task_usage_rule",
    "strict_supervisor_conclusion",
]

MANIFEST_FIELDNAMES = [
    "task_id",
    "task_name",
    "task_question",
    "fit_primary_count",
    "fit_auxiliary_count",
    "reference_only_count",
    "locked_holdout_count",
    "strict_task_usage_rule",
]


WINDOW_TASK_MAP: dict[str, list[str]] = {
    "ca_train_window_001": ["ca_task_003", "ca_task_004", "ca_task_005"],
    "ca_train_window_002": [
        "ca_task_001",
        "ca_task_002",
        "ca_task_003",
        "ca_task_004",
        "ca_task_005",
        "ca_task_006",
    ],
    "ca_train_window_003": ["ca_task_002", "ca_task_003", "ca_task_004", "ca_task_005"],
    "ca_train_window_004": ["ca_task_004", "ca_task_005"],
    "ca_train_window_005": ["ca_task_002", "ca_task_003", "ca_task_004", "ca_task_005"],
    "ca_train_window_006": ["ca_task_002", "ca_task_004", "ca_task_005"],
    "ca_train_window_007": ["ca_task_001", "ca_task_006"],
    "ca_train_window_008": ["ca_task_003", "ca_task_006"],
    "ca_train_window_009": ["ca_task_002", "ca_task_006"],
    "ca_train_window_010": ["ca_task_004", "ca_task_005"],
}


def _task_rule(sample_window_id: str, task_id: str) -> str:
    if sample_window_id == "ca_train_window_002":
        return "Keep as locked holdout for every task until exact January ignition wording is locked."
    if sample_window_id == "ca_train_window_007":
        return "Use only as positive-reference context; do not fit until the cleaner January ignition archetype unlocks."
    if sample_window_id == "ca_train_window_008":
        return "Use only for subwindow diffusion-decay reference; do not fit as a full durable conference-chain leg."
    if sample_window_id == "ca_train_window_010":
        return "Use only as launch-milestone negative reference; do not fit as a primary negative archetype."
    if sample_window_id == "ca_train_window_009":
        return "Allow only as auxiliary bridge sample for novelty and diffusion tasks, not as durable main-leg fit."
    if sample_window_id == "ca_train_window_006":
        return "Allow only as auxiliary negative for capital-mapping misalignment and structure-gate tasks."
    if sample_window_id == "ca_train_window_004":
        return "Allow only as negative-support sample for capital and structure tasks; real anchor does not imply tradability."
    if sample_window_id == "ca_train_window_001":
        return "Allow only as supportive early-board-width positive context for breadth, capital, and structure tasks."
    if task_id == "ca_task_002":
        return "Use as clean negative new-leg-vs-echo fit sample."
    return "Use as clean negative fit sample under the current strict task boundary."


def _usage_fields(row: dict[str, str]) -> dict[str, Any]:
    package_tier = row["package_tier"]
    sample_weight = float(row["sample_weight"])
    if package_tier == "primary_fit":
        return {
            "task_usage_tier": "fit_primary",
            "allow_in_task_fit": 1,
            "allow_as_task_reference": 0,
            "allow_as_task_holdout": 0,
            "task_sample_weight": sample_weight,
        }
    if package_tier == "auxiliary_fit":
        return {
            "task_usage_tier": "fit_auxiliary",
            "allow_in_task_fit": 1,
            "allow_as_task_reference": 0,
            "allow_as_task_holdout": 0,
            "task_sample_weight": sample_weight,
        }
    if package_tier == "reference_only":
        return {
            "task_usage_tier": "reference_only",
            "allow_in_task_fit": 0,
            "allow_as_task_reference": 1,
            "allow_as_task_holdout": 0,
            "task_sample_weight": 0.0,
        }
    if package_tier == "locked_holdout":
        return {
            "task_usage_tier": "locked_holdout",
            "allow_in_task_fit": 0,
            "allow_as_task_reference": 0,
            "allow_as_task_holdout": 1,
            "task_sample_weight": 0.0,
        }
    raise KeyError(f"Unhandled package tier: {package_tier}")


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    package_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_sample_package_v1.csv"
    )
    task_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_task_definition_v1.csv"
    )
    package_rows = _read_csv(package_path)
    task_rows = _read_csv(task_path)
    if not package_rows or not task_rows:
        raise FileNotFoundError("Training sample package or task definition is missing.")

    task_map = {row["task_id"]: row for row in task_rows}
    output_rows: list[dict[str, Any]] = []
    for package_row in package_rows:
        sample_window_id = package_row["sample_window_id"]
        window_tasks = WINDOW_TASK_MAP.get(sample_window_id)
        if not window_tasks:
            raise KeyError(f"No task map configured for {sample_window_id}")
        usage_fields = _usage_fields(package_row)
        for task_id in window_tasks:
            task_row = task_map[task_id]
            output_rows.append(
                {
                    "task_id": task_id,
                    "task_name": task_row["task_name"],
                    "sample_window_id": sample_window_id,
                    "window_name": package_row["window_name"],
                    "training_role": package_row["training_role"],
                    "package_tier": package_row["package_tier"],
                    "package_usage_mode": package_row["package_usage_mode"],
                    "task_usage_tier": usage_fields["task_usage_tier"],
                    "allow_in_task_fit": usage_fields["allow_in_task_fit"],
                    "allow_as_task_reference": usage_fields["allow_as_task_reference"],
                    "allow_as_task_holdout": usage_fields["allow_as_task_holdout"],
                    "task_sample_weight": usage_fields["task_sample_weight"],
                    "strict_task_usage_rule": _task_rule(sample_window_id, task_id),
                    "strict_supervisor_conclusion": package_row["strict_supervisor_conclusion"],
                }
            )

    manifest_rows: list[dict[str, Any]] = []
    for task_row in task_rows:
        task_id = task_row["task_id"]
        task_export_rows = [row for row in output_rows if row["task_id"] == task_id]
        manifest_rows.append(
            {
                "task_id": task_id,
                "task_name": task_row["task_name"],
                "task_question": task_row["primary_question"],
                "fit_primary_count": sum(1 for row in task_export_rows if row["task_usage_tier"] == "fit_primary"),
                "fit_auxiliary_count": sum(1 for row in task_export_rows if row["task_usage_tier"] == "fit_auxiliary"),
                "reference_only_count": sum(
                    1 for row in task_export_rows if row["task_usage_tier"] == "reference_only"
                ),
                "locked_holdout_count": sum(
                    1 for row in task_export_rows if row["task_usage_tier"] == "locked_holdout"
                ),
                "strict_task_usage_rule": (
                    "This manifest keeps task fitting explainable: only explicit fit tiers are trainable, "
                    "reference windows stay non-fit, and window 002 remains locked out across every task."
                ),
            }
        )

    return output_rows, manifest_rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    export_rows, manifest_rows = materialize(repo_root)
    export_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_training_task_ready_export_v1.csv"
    )
    manifest_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_training_task_ready_manifest_v1.csv"
    )
    _write_csv(export_path, export_rows, EXPORT_FIELDNAMES)
    _write_csv(manifest_path, manifest_rows, MANIFEST_FIELDNAMES)
    print(f"materialized {len(export_rows)} rows -> {export_path}")
    print(f"materialized {len(manifest_rows)} rows -> {manifest_path}")


if __name__ == "__main__":
    main()
