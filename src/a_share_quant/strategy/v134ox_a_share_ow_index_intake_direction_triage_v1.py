from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134OXAShareOWIndexIntakeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134OXAShareOWIndexIntakeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.checklist_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_index_daily_source_intake_checklist_v1.csv"
        )

    def analyze(self) -> V134OXAShareOWIndexIntakeDirectionTriageV1Report:
        rows = _read_csv(self.checklist_path)
        summary = {
            "intake_step_count": len(rows),
            "closed_step_count": sum(row["current_state"] == "closed" for row in rows),
            "authoritative_status": "index_daily_future_progress_should_be_handled_as_source_intake_then_reopen_not_as_internal_replay_iteration",
        }
        triage_rows = [
            {"component": "source_arrival", "direction": "wait_for_new_raw_index_source_before_any_reopen"},
            {"component": "horizon_match", "direction": "verify_new_source_reaches_shadow_horizon_before_materialization"},
            {"component": "materialization_review", "direction": "reopen_index_daily_materialization_only_after_source_intake_success"},
            {"component": "paired_surface_review", "direction": "recheck_daily_market_promotion_only_after_index_daily_boundary_moves"},
        ]
        interpretation = [
            "Replay-side movement is now fully governed by a future source-intake checklist.",
            "Further internal replay modeling without new source arrival would be drift.",
        ]
        return V134OXAShareOWIndexIntakeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OXAShareOWIndexIntakeDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OXAShareOWIndexIntakeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ox_a_share_ow_index_intake_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
