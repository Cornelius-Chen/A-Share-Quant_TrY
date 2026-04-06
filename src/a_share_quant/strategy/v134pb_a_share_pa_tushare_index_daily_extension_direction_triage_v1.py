from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.report_path = (
            repo_root / "reports" / "analysis" / "v134pa_a_share_tushare_index_daily_extension_bootstrap_v1.json"
        )

    def analyze(self) -> V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Report:
        report = json.loads(self.report_path.read_text(encoding="utf-8"))
        summary = report["summary"]
        triage_rows = [
            {"component": "raw_source", "direction": "treat_tushare_index_daily_extension_as_active_new_raw_source"},
            {"component": "replay_reaudit", "direction": "rerun_index_daily_gap_and_paired_surface_chain_immediately"},
            {"component": "promotion_governance", "direction": "do_not_assume_live_like_opening_just_from_raw_source_arrival"},
        ]
        result_summary = {
            "row_count": summary["row_count"],
            "coverage_end": summary["coverage_end"],
            "authoritative_status": "tushare_index_daily_extension_should_now_be_consumed_as_new_replay_side_source",
        }
        interpretation = [
            "The replay-side source boundary has moved materially once this raw file is present.",
            "The correct next action is re-audit of downstream blockers rather than keeping the old true-source-gap narrative.",
        ]
        return V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Report(
            result_summary, triage_rows, interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PBASharePATushareIndexDailyExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pb_a_share_pa_tushare_index_daily_extension_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
