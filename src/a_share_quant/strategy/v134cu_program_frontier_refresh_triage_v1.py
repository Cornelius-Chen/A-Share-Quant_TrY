from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CUProgramFrontierRefreshTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CUProgramFrontierRefreshTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.frontier_path = (
            repo_root / "reports" / "analysis" / "v134ct_commercial_aerospace_frontier_status_card_v1.json"
        )
        self.output_csv = repo_root / "data" / "training" / "program_frontier_refresh_triage_v1.csv"

    def analyze(self) -> V134CUProgramFrontierRefreshTriageV1Report:
        frontier = json.loads(self.frontier_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "commercial_aerospace_reduce",
                "status": "frozen_in_program_view",
                "detail": "Program-level reading must now treat reduce as frozen and no longer as an open semantic branch.",
            },
            {
                "component": "commercial_aerospace_intraday_add",
                "status": "next_but_deferred",
                "detail": "Program-level reading should mark intraday add as the next frontier, but still deferred until an explicit shift is authorized.",
            },
            {
                "component": "current_instruction",
                "status": "respect_deferred_shift",
                "detail": "Do not silently start intraday add simply because reduce is frozen; wait for the later deliberate opening.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134cu_program_frontier_refresh_triage_v1",
            "authoritative_status": "program_view_refreshed_reduce_frozen_intraday_add_deferred",
            "next_frontier": frontier["summary"]["next_frontier"],
            "next_frontier_state": frontier["summary"]["next_frontier_state"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CU refreshes the program-level frontier reading after reduce handoff completion.",
            "The result is intentionally conservative: the next frontier is named, but not opened by implication.",
        ]
        return V134CUProgramFrontierRefreshTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CUProgramFrontierRefreshTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CUProgramFrontierRefreshTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cu_program_frontier_refresh_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
