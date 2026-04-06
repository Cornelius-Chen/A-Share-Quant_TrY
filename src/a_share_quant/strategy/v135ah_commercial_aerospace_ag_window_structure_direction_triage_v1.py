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
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows}


class V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_training_admission_summary_v1.csv"
        )

    def analyze(self) -> V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Report:
        rows = _read_csv(self.summary_path)
        if not rows:
            raise FileNotFoundError(self.summary_path)
        triage_rows: list[dict[str, Any]] = []
        for row in rows:
            if row["admission_state"] == "hold_until_policy_wording_locked":
                recommendation = "keep_window_off_final_training_until_january_policy_text_is_locked"
            elif row["admission_state"] == "subwindow_ready_but_full_window_not_ready":
                recommendation = "allow_subwindow_learning_only_and_continue_february_followthrough_backfill"
            else:
                recommendation = "allow_negative_sample_training_and_keep_launch_chain_expansion_under_review"
            triage_rows.append(
                {
                    "sample_window_id": row["sample_window_id"],
                    "admission_state": row["admission_state"],
                    "recommendation": recommendation,
                }
            )
        summary = {
            "window_count": len(rows),
            "ready_negative_sample_count": sum(
                1 for row in rows if row["admission_state"] == "negative_sample_ready"
            ),
            "policy_hold_count": sum(
                1 for row in rows if row["admission_state"] == "hold_until_policy_wording_locked"
            ),
            "partial_subwindow_count": sum(
                1 for row in rows if row["admission_state"] == "subwindow_ready_but_full_window_not_ready"
            ),
        }
        return V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ah_commercial_aerospace_ag_window_structure_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
