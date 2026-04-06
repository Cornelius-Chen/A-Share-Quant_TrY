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
class V134OTAShareOSBuildCompletionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134OTAShareOSBuildCompletionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.report_path = repo_root / "data" / "training" / "a_share_information_center_build_completion_status_v1.csv"

    def analyze(self) -> V134OTAShareOSBuildCompletionDirectionTriageV1Report:
        rows = _read_csv(self.report_path)
        values = {row["metric"]: int(row["value"]) for row in rows}
        triage_rows = [
            {
                "component": "core_build",
                "direction": "treat_information_center_core_as_built_complete_enough",
            },
            {
                "component": "source_side",
                "direction": "advance_only_via_manual_closure_not_via_more_registry_buildout",
            },
            {
                "component": "replay_side",
                "direction": "treat_replay_extension_as_opened_past_source_gap_and_limit_halt_derivation_with_a_controlled_promotable_subset",
            },
            {
                "component": "execution_live_like",
                "direction": "retain_intentional_block_until_source_side_and_replay_side_stoplines_move",
            },
        ]
        result_summary = {
            "foundation_complete_count": values["foundation_complete_count"],
            "global_blocker_count": values["total_blocker_count"],
            "authoritative_status": "information_center_should_now_be_managed_as_completed_core_plus_gated_residual_closure",
        }
        interpretation = [
            "The project should no longer be narrated as unfinished core construction.",
            "The correct framing is completed core build with explicitly gated residual closure work.",
        ]
        return V134OTAShareOSBuildCompletionDirectionTriageV1Report(
            summary=result_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OTAShareOSBuildCompletionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OTAShareOSBuildCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ot_a_share_os_build_completion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
