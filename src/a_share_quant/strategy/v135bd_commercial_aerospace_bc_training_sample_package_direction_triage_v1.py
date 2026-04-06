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
class V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows}


class V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.package_path = (
            repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_sample_package_v1.csv"
        )

    def analyze(self) -> V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Report:
        rows = _read_csv(self.package_path)
        if not rows:
            raise FileNotFoundError(self.package_path)
        triage_rows = []
        for row in rows:
            tier = row["package_tier"]
            if tier == "primary_fit":
                recommendation = "fit_directly_under_current_negative_role"
            elif tier == "auxiliary_fit":
                recommendation = "fit_as_auxiliary_context_only"
            elif tier == "reference_only":
                recommendation = "keep_for_reference_and_subwindow_learning_only"
            else:
                recommendation = "keep_locked_out_of_fit"
            triage_rows.append(
                {
                    "sample_window_id": row["sample_window_id"],
                    "package_tier": tier,
                    "recommendation": recommendation,
                }
            )
        summary = {
            "window_count": len(rows),
            "primary_fit_count": sum(1 for row in rows if row["package_tier"] == "primary_fit"),
            "auxiliary_fit_count": sum(1 for row in rows if row["package_tier"] == "auxiliary_fit"),
            "non_fit_count": sum(1 for row in rows if row["package_tier"] in {"reference_only", "locked_holdout"}),
        }
        return V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135bd_commercial_aerospace_bc_training_sample_package_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
