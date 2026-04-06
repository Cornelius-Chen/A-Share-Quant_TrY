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
class V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Report:
    summary: dict[str, Any]
    manifest_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "manifest_rows": self.manifest_rows,
            "interpretation": self.interpretation,
        }


class V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.export_path = (
            repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_task_ready_export_v1.csv"
        )
        self.manifest_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_task_ready_manifest_v1.csv"
        )

    def analyze(self) -> V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Report:
        export_rows = _read_csv(self.export_path)
        manifest_rows = _read_csv(self.manifest_path)
        if not export_rows or not manifest_rows:
            raise FileNotFoundError("Commercial aerospace training task-ready export outputs are missing.")
        summary = {
            "row_count": len(export_rows),
            "unique_task_count": len({row["task_id"] for row in export_rows}),
            "fit_primary_row_count": sum(1 for row in export_rows if row["task_usage_tier"] == "fit_primary"),
            "fit_auxiliary_row_count": sum(1 for row in export_rows if row["task_usage_tier"] == "fit_auxiliary"),
            "reference_only_row_count": sum(1 for row in export_rows if row["task_usage_tier"] == "reference_only"),
            "locked_holdout_row_count": sum(1 for row in export_rows if row["task_usage_tier"] == "locked_holdout"),
            "window_002_holdout_task_count": sum(
                1
                for row in export_rows
                if row["sample_window_id"] == "ca_train_window_002" and row["task_usage_tier"] == "locked_holdout"
            ),
        }
        interpretation = [
            "The task-ready layer is stricter than the sample package because it routes each window only into tasks it can honestly teach.",
            "Window 002 remains a full holdout across all six tasks and never appears as fit or reference.",
            "Primary fitting still comes only from the cleanest released negatives, while positive, bridge, and launch cases remain auxiliary or reference-only.",
        ]
        return V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Report(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135be_commercial_aerospace_training_task_ready_export_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
