from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v131g_commercial_aerospace_intraday_data_readiness_gap_audit_v1 import (
    V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer,
)
from a_share_quant.strategy.v131h_commercial_aerospace_intraday_collection_manifest_v1 import (
    V131HCommercialAerospaceIntradayCollectionManifestAnalyzer,
)


@dataclass(slots=True)
class V131JCommercialAerospaceIntradayCollectionChangeGateReport:
    summary: dict[str, Any]
    artifact_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "artifact_rows": self.artifact_rows,
            "interpretation": self.interpretation,
        }


class V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.minute_dir = repo_root / "data" / "raw" / "minute_bars"

    def analyze(self) -> V131JCommercialAerospaceIntradayCollectionChangeGateReport:
        readiness = V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer(self.repo_root).analyze()
        manifest = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(self.repo_root).analyze()

        symbol_priority = {
            row["symbol"]: row["priority"]
            for row in manifest.manifest_rows
        }
        artifact_rows: list[dict[str, Any]] = []
        for row in readiness.symbol_rows:
            symbol = row["symbol"]
            expected_path = self.minute_dir / f"sina_{symbol}_recent_1min_v1.csv"
            artifact_rows.append(
                {
                    "symbol": symbol,
                    "required_role": row["required_role"],
                    "priority": symbol_priority.get(symbol, "medium"),
                    "expected_artifact_type": "recent_1min_local_csv",
                    "expected_artifact_path": str(expected_path.relative_to(self.repo_root)),
                    "currently_present": row["minute_support_present"],
                    "change_event_that_opens_gate": f"{symbol}_minute_file_arrives",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v131j_commercial_aerospace_intraday_collection_change_gate_v1",
            "required_artifact_count": len(artifact_rows),
            "present_artifact_count": sum(1 for row in artifact_rows if row["currently_present"]),
            "missing_artifact_count": sum(1 for row in artifact_rows if not row["currently_present"]),
            "authoritative_status": "intraday_collection_change_gate_installed",
            "authoritative_rule": "only reopen commercial-aerospace intraday override modeling after all required minute artifacts are present",
        }
        interpretation = [
            "V1.31J converts the intraday collection manifest into an explicit file-based change gate.",
            "This prevents premature intraday modeling under partial minute coverage and makes the unblock condition mechanical.",
        ]
        return V131JCommercialAerospaceIntradayCollectionChangeGateReport(
            summary=summary,
            artifact_rows=artifact_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131JCommercialAerospaceIntradayCollectionChangeGateReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131j_commercial_aerospace_intraday_collection_change_gate_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
