from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v131j_commercial_aerospace_intraday_collection_change_gate_v1 import (
    V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer,
)
from a_share_quant.strategy.v131i_commercial_aerospace_intraday_data_governance_triage_v1 import (
    V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer,
)


@dataclass(slots=True)
class V131KCommercialAerospaceIntradayCollectionStatusCardReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_collection_status_card_v1.csv"
        )

    def analyze(self) -> V131KCommercialAerospaceIntradayCollectionStatusCardReport:
        gate = V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer(self.repo_root).analyze()
        governance = V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer(self.repo_root).analyze()

        status_rows = [
            {
                "program_branch": "commercial_aerospace_intraday_override",
                "status": "blocked",
                "missing_required_artifacts": gate.summary["missing_artifact_count"],
                "required_artifacts": gate.summary["required_artifact_count"],
                "next_action": "collect_required_minute_files_then_rerun_intraday_chain",
                "highest_priority_missing_symbols": "/".join(
                    row["symbol"]
                    for row in gate.artifact_rows
                    if (not row["currently_present"] and row["priority"] == "high")
                ),
                "authoritative_status": governance.summary["authoritative_status"],
            }
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            for row in status_rows:
                writer.writerow(row)

        summary = {
            "acceptance_posture": "freeze_v131k_commercial_aerospace_intraday_collection_status_card_v1",
            "program_status": "blocked_for_minute_data",
            "required_artifact_count": gate.summary["required_artifact_count"],
            "present_artifact_count": gate.summary["present_artifact_count"],
            "missing_artifact_count": gate.summary["missing_artifact_count"],
            "highest_priority_missing_symbols": [
                row["symbol"]
                for row in gate.artifact_rows
                if (not row["currently_present"] and row["priority"] == "high")
            ],
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "treat the commercial-aerospace intraday branch as blocked until the required minute artifact count reaches full coverage",
        }
        interpretation = [
            "V1.31K compresses the intraday branch into a single operational status card.",
            "It is the minute-data analogue of the frozen transfer status card: blocked now, mechanically unblocked later.",
        ]
        return V131KCommercialAerospaceIntradayCollectionStatusCardReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131KCommercialAerospaceIntradayCollectionStatusCardReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131k_commercial_aerospace_intraday_collection_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
