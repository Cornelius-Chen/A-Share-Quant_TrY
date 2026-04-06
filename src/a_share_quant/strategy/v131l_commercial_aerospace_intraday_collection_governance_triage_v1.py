from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v131j_commercial_aerospace_intraday_collection_change_gate_v1 import (
    V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer,
)
from a_share_quant.strategy.v131k_commercial_aerospace_intraday_collection_status_card_v1 import (
    V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer,
)


@dataclass(slots=True)
class V131LCommercialAerospaceIntradayCollectionGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V131LCommercialAerospaceIntradayCollectionGovernanceTriageReport:
        gate = V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer(self.repo_root).analyze()
        card = V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer(self.repo_root).analyze()

        triage_rows = [
            {
                "component": "intraday_override_supervision_bundle",
                "status": "retain",
                "rationale": "the governance bundle is ready and should be preserved as the seed geometry for future minute-level work",
            },
            {
                "component": "minute_data_collection_gate",
                "status": "installed",
                "rationale": "all four required symbol files are missing, so the unblock condition must stay mechanical rather than discretionary",
            },
            {
                "component": "intraday_modeling",
                "status": "blocked",
                "rationale": "do not open intraday modeling until coverage reaches full support across the required failure-seed symbols",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v131l_commercial_aerospace_intraday_collection_governance_triage_v1",
            "authoritative_status": "freeze_intraday_collection_governance_until_required_minute_files_arrive",
            "required_artifact_count": gate.summary["required_artifact_count"],
            "missing_artifact_count": gate.summary["missing_artifact_count"],
            "program_status": card.summary["program_status"],
            "authoritative_rule": "retain the intraday branch as governance plus collection state, and reopen modeling only when the file-based minute-data gate is fully satisfied",
        }
        interpretation = [
            "V1.31L freezes the commercial-aerospace intraday branch into a governance-and-collection posture.",
            "This is the honest next state: useful supervision exists, but lawful modeling remains blocked by missing minute artifacts.",
        ]
        return V131LCommercialAerospaceIntradayCollectionGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131LCommercialAerospaceIntradayCollectionGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131l_commercial_aerospace_intraday_collection_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
