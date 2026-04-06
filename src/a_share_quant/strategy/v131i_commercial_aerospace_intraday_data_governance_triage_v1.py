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
class V131ICommercialAerospaceIntradayDataGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V131ICommercialAerospaceIntradayDataGovernanceTriageReport:
        readiness = V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer(self.repo_root).analyze()
        manifest = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(self.repo_root).analyze()

        missing_count = int(readiness.summary["missing_required_symbol_count"])
        keep_blocked = missing_count > 0

        triage_rows = [
            {
                "component": "commercial_aerospace_intraday_override_modeling",
                "status": "blocked_for_now" if keep_blocked else "unblocked_for_next_stage",
                "rationale": "minute-level prototype should not start until required failure-seed symbols have local minute-bar support",
            },
            {
                "component": "collection_priority",
                "status": "retained_manifest",
                "rationale": "collect retained override positives first, then reversal watches, using the exact execution-session windows in the manifest",
            },
            {
                "component": "current_eod_primary",
                "status": "keep_frozen",
                "rationale": "the intraday governance branch is additive supervision work and must not reopen lawful EOD replay tuning",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v131i_commercial_aerospace_intraday_data_governance_triage_v1",
            "authoritative_status": (
                "keep_intraday_override_governance_bundle_but_block_intraday_modeling_until_minute_data_arrives"
                if keep_blocked
                else "minute_data_ready_for_next_intraday_stage"
            ),
            "missing_required_symbol_count": readiness.summary["missing_required_symbol_count"],
            "missing_required_symbols": readiness.summary["missing_required_symbols"],
            "manifest_row_count": manifest.summary["manifest_row_count"],
            "authoritative_rule": "preserve the intraday supervision bundle and collection manifest, but do not start intraday modeling before local minute support closes the required-symbol gap",
        }
        interpretation = [
            "V1.31I closes the loop between the supervision bundle and the data layer.",
            "It answers the practical next-step question: can intraday modeling start now, or should the work remain frozen behind a minute-data gap?",
        ]
        return V131ICommercialAerospaceIntradayDataGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131ICommercialAerospaceIntradayDataGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131ICommercialAerospaceIntradayDataGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131i_commercial_aerospace_intraday_data_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
