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
class V135AICommercialAerospaceWindowLeaderFollowerAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AICommercialAerospaceWindowLeaderFollowerAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.structure_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_leader_follower_structure_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_leader_follower_summary_v1.csv"
        )

    def analyze(self) -> V135AICommercialAerospaceWindowLeaderFollowerAuditV1Report:
        rows = _read_csv(self.structure_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Leader/follower commercial aerospace training outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "december_leader_count": sum(1 for row in rows if row["leader_follower_class"] == "leader"),
            "december_follower_count": sum(1 for row in rows if row["leader_follower_class"] == "follower"),
            "february_leader_deterioration_count": sum(
                1 for row in rows if row["leader_follower_class"] == "leader_deterioration"
            ),
            "february_follower_failure_count": sum(
                1 for row in rows if row["leader_follower_class"] == "follower_failure"
            ),
            "full_window_hold_count": sum(
                1
                for row in summary_rows
                if row["final_training_admission"] == "subwindow_ready_but_full_window_not_ready"
            ),
        }
        interpretation = [
            "Window 008 is now split into a December selective-diffusion map and a February failed-followthrough map.",
            "The most important negative evidence is that the best December leader also broke in February.",
            "This artifact clarifies why the meeting chain is useful for subwindow learning but still not fit for a full-window final-training pass.",
        ]
        return V135AICommercialAerospaceWindowLeaderFollowerAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AICommercialAerospaceWindowLeaderFollowerAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AICommercialAerospaceWindowLeaderFollowerAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ai_commercial_aerospace_window_leader_follower_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
