from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_path = (
            repo_root / "reports" / "analysis" / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cv_reduce_do_not_drift_triage_v1.csv"
        )

    def analyze(self) -> V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Report:
        status = json.loads(self.status_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "reduce_mainline",
                "status": "do_not_drift",
                "detail": "Do not reopen broad reduce tuning; the branch is frozen as complete enough for research.",
            },
            {
                "component": "residue_cases",
                "status": "local_only",
                "detail": "Only local residue supervision is still allowed inside reduce.",
            },
            {
                "component": "execution_closure",
                "status": "wait_for_infrastructure",
                "detail": f"execution_blocker_count = {status['summary']['execution_blocker_count']}",
            },
            {
                "component": "future_frontier",
                "status": "deferred_next_step",
                "detail": "The next frontier is intraday add, but it remains deferred until the later explicit shift.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134cw_commercial_aerospace_cv_reduce_do_not_drift_triage_v1",
            "authoritative_status": "reduce_branch_frozen_do_not_drift_wait_for_later_intraday_add_shift",
            "execution_blocker_count": status["summary"]["execution_blocker_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CW converts the final reduce status card into an explicit do-not-drift judgment.",
            "The branch should now be treated as frozen operationally, not merely conceptually.",
        ]
        return V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cw_commercial_aerospace_cv_reduce_do_not_drift_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
