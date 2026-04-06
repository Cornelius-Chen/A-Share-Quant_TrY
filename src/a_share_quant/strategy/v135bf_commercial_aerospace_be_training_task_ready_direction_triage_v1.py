from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{str(k).lstrip("\ufeff"): v for k, v in row.items()} for row in csv.DictReader(handle)]


@dataclass(slots=True)
class V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows}


class V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.manifest_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_task_ready_manifest_v1.csv"
        )

    def _recommendation(self, row: dict[str, str]) -> str:
        task_id = row["task_id"]
        fit_primary_count = int(row["fit_primary_count"])
        fit_auxiliary_count = int(row["fit_auxiliary_count"])
        reference_only_count = int(row["reference_only_count"])
        locked_holdout_count = int(row["locked_holdout_count"])

        if task_id == "ca_task_001":
            return "use_reference_and_holdout_only_until_primary_positive_archetype_unlocks"
        if task_id == "ca_task_006":
            return "fit_bridge_auxiliary_cautiously_and_keep_positive_examples_as_reference_only"
        if fit_primary_count >= 2 and fit_auxiliary_count >= 2:
            return "fit_direct_negatives_with_auxiliary_context_under_current_strict_boundary"
        if fit_auxiliary_count > 0 and reference_only_count > 0 and locked_holdout_count > 0:
            return "use_mixed_auxiliary_reference_stack_but_keep_policy_holdout_locked"
        return "keep_current_task_boundary_without_promotion"

    def analyze(self) -> V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Report:
        rows = _read_csv(self.manifest_path)
        if not rows:
            raise FileNotFoundError(self.manifest_path)
        triage_rows = []
        for row in rows:
            triage_rows.append(
                {
                    "task_id": row["task_id"],
                    "task_name": row["task_name"],
                    "recommendation": self._recommendation(row),
                }
            )
        summary = {
            "task_count": len(rows),
            "tasks_with_primary_fit": sum(1 for row in rows if int(row["fit_primary_count"]) > 0),
            "tasks_with_auxiliary_fit": sum(1 for row in rows if int(row["fit_auxiliary_count"]) > 0),
            "tasks_with_reference_only": sum(1 for row in rows if int(row["reference_only_count"]) > 0),
            "tasks_with_locked_holdout": sum(1 for row in rows if int(row["locked_holdout_count"]) > 0),
        }
        return V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135bf_commercial_aerospace_be_training_task_ready_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
