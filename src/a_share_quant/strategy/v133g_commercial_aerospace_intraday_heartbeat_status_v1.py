from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133GCommercialAerospaceIntradayHeartbeatStatusReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V133GCommercialAerospaceIntradayHeartbeatStatusAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.gate_path = (
            repo_root / "reports" / "analysis" / "v133f_commercial_aerospace_intraday_reopen_change_gate_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_heartbeat_status_v1.csv"
        )

    def analyze(self) -> V133GCommercialAerospaceIntradayHeartbeatStatusReport:
        gate = json.loads(self.gate_path.read_text(encoding="utf-8"))

        status_rows = [
            {
                "component": "intraday_execution_lane",
                "status": "frozen",
                "detail": "governance package ready but execution infrastructure still blocked",
            },
            {
                "component": "current_primary_variant",
                "status": "tail_weakdrift_full",
                "detail": "lawful EOD primary remains authoritative and isolated from minute execution work",
            },
            {
                "component": "rerun_required",
                "status": str(gate["summary"]["rerun_required"]),
                "detail": "intraday reopening should not start until the explicit change gate changes state",
            },
            {
                "component": "missing_artifact_count",
                "status": str(gate["summary"]["missing_artifact_count"]),
                "detail": "number of missing infrastructure pieces before intraday execution can reopen",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v133g_commercial_aerospace_intraday_heartbeat_status_v1",
            "program_status": "frozen",
            "rerun_required": gate["summary"]["rerun_required"],
            "missing_artifact_count": gate["summary"]["missing_artifact_count"],
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the commercial-aerospace intraday lane should present a compact frozen heartbeat until the explicit execution change gate opens",
        }
        interpretation = [
            "V1.33G packages the commercial-aerospace intraday freeze into a heartbeat-style status card.",
            "The point is to make the branch's frozen state operationally obvious rather than implicit.",
        ]
        return V133GCommercialAerospaceIntradayHeartbeatStatusReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133GCommercialAerospaceIntradayHeartbeatStatusReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133GCommercialAerospaceIntradayHeartbeatStatusAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133g_commercial_aerospace_intraday_heartbeat_status_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
