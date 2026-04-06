from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.package_path = (
            repo_root / "reports" / "analysis" / "v134cn_commercial_aerospace_reduce_handoff_package_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cn_reduce_handoff_direction_triage_v1.csv"
        )

    def analyze(self) -> V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Report:
        package = json.loads(self.package_path.read_text(encoding="utf-8"))
        summary = package["summary"]

        triage_rows = [
            {
                "component": "reduce_branch",
                "status": "freeze_mainline",
                "detail": "Treat reduce as frozen mainline research rather than an open semantic frontier.",
            },
            {
                "component": "residue_policy",
                "status": "local_maintenance_only",
                "detail": "Only local residue supervision remains justified inside reduce; do not reopen broad tuning.",
            },
            {
                "component": "execution_policy",
                "status": "still_blocked_by_infrastructure",
                "detail": f"execution_blocker_count = {summary['execution_blocker_count']}",
            },
            {
                "component": "future_handoff",
                "status": "approved_but_not_triggered_now",
                "detail": "The branch is ready for a later handoff to intraday add, but this step does not start that frontier.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1",
            "authoritative_status": "freeze_reduce_handoff_package_and_do_not_reopen_reduce_mainline_before_future_frontier_shift",
            "execution_blocker_count": summary["execution_blocker_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CO converts the reduce handoff package into the final direction judgment for the current frontier.",
            "The branch should now treat reduce as frozen mainline research, with only local maintenance allowed until a later frontier shift is intentionally opened.",
        ]
        return V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
