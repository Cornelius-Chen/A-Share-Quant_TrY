from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133DCommercialAerospaceIntradayExecutionStatusCardReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V133DCommercialAerospaceIntradayExecutionStatusCardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = (
            repo_root / "reports" / "analysis" / "v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_execution_status_card_v1.csv"
        )

    def analyze(self) -> V133DCommercialAerospaceIntradayExecutionStatusCardReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
        requirement_rows = protocol["requirement_rows"]

        status_rows = []
        for row in requirement_rows:
            if row["status"] == "blocked":
                status_rows.append(
                    {
                        "component": row["requirement"],
                        "status": "blocked",
                        "why": row["current_state"],
                        "next": row["unlock_condition"],
                    }
                )
            else:
                status_rows.append(
                    {
                        "component": row["requirement"],
                        "status": "ready",
                        "why": row["current_state"],
                        "next": row["unlock_condition"],
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        blocked_rows = [row for row in status_rows if row["status"] == "blocked"]
        summary = {
            "acceptance_posture": "freeze_v133d_commercial_aerospace_intraday_execution_status_card_v1",
            "intraday_execution_status": "blocked" if blocked_rows else "ready",
            "blocked_component_count": len(blocked_rows),
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "commercial aerospace should not reopen local intraday execution work until the explicit unblock protocol changes state",
        }
        interpretation = [
            "V1.33D packages the intraday-execution blockers into a compact status card.",
            "The goal is to prevent ambiguous continuation work once the minute governance package has already been completed.",
        ]
        return V133DCommercialAerospaceIntradayExecutionStatusCardReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133DCommercialAerospaceIntradayExecutionStatusCardReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133DCommercialAerospaceIntradayExecutionStatusCardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133d_commercial_aerospace_intraday_execution_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
