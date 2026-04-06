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
class V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows}


class V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.ledger_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_admission_ledger_v1.csv"
        )

    def analyze(self) -> V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Report:
        rows = _read_csv(self.ledger_path)
        if not rows:
            raise FileNotFoundError(self.ledger_path)
        triage_rows = []
        for row in rows:
            training_class = row["training_admission_class"]
            if training_class == "policy_gate_hold":
                recommendation = "keep_hold_and_continue_policy_wording_lock"
            elif training_class == "subwindow_learning_only":
                recommendation = "allow_subwindow_learning_only"
            elif training_class in {
                "positive_support_sample_ready",
                "negative_support_sample_ready",
                "positive_sample_ready",
                "negative_sample_ready",
                "bridge_sample_ready",
            }:
                recommendation = "allow_training_under_current_role"
            else:
                recommendation = "keep_under_review_and_do_not_release"
            triage_rows.append(
                {
                    "sample_window_id": row["sample_window_id"],
                    "training_admission_class": training_class,
                    "recommendation": recommendation,
                }
            )
        summary = {
            "window_count": len(rows),
            "released_count": sum(
                1
                for row in rows
                if row["supervisor_release_state"] in {"released", "released_but_not_final", "released_as_subwindow_only"}
            ),
            "hold_count": sum(1 for row in rows if row["supervisor_release_state"] == "hold"),
            "under_review_count": sum(1 for row in rows if row["supervisor_release_state"] == "not_released"),
        }
        return V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135av_commercial_aerospace_au_training_admission_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
