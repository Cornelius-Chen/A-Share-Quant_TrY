from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1.json"
        )

    def analyze(self) -> V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "raw_data_coverage",
                "status": "retain",
                "rationale": "raw daily and intraday coverage already continue past lockout end",
            },
            {
                "component": "execution_history_cutoff",
                "status": "not_primary_blocker",
                "rationale": "execution history ends on 20260227, but derived board surfaces continue to 20260320, so the current stop is not merely an execution cutoff",
            },
            {
                "component": "lockout_aligned_derivation_boundary",
                "status": "dominant_reading",
                "rationale": "both daily-state and phase-geometry surfaces stop exactly at lockout end while raw data continues beyond it",
            },
            {
                "component": "shadow_bridge",
                "status": "keep_blocked",
                "rationale": "reentry-to-add handoff remains blocked until the lockout-aligned derivation boundary is explicitly extended",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "boundary classification clarifies governance but does not authorize execution",
            },
        ]
        interpretation = [
            "V1.34HC turns the boundary classification into the current direction verdict.",
            "The next justified move is not to debate post-lockout unlock quality in the abstract, but to decide whether the lockout-aligned derivation boundary should remain frozen or be explicitly extended.",
        ]
        return V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134hc_commercial_aerospace_hb_boundary_direction_triage_v1",
                "authoritative_status": (
                    "retain_derivation_boundary_classification_and_keep_shadow_bridge_blocked_until_boundary_policy_changes"
                ),
                "orders_last_trade_date": audit["summary"]["orders_last_trade_date"],
                "daily_state_last_trade_date": audit["summary"]["daily_state_last_trade_date"],
                "phase_table_last_trade_date": audit["summary"]["phase_table_last_trade_date"],
                "raw_daily_last_trade_date": audit["summary"]["raw_daily_last_trade_date"],
                "raw_intraday_last_trade_date": audit["summary"]["raw_intraday_last_trade_date"],
                "lockout_end_trade_date": audit["summary"]["lockout_end_trade_date"],
                "derived_stop_matches_lockout_end": audit["summary"]["derived_stop_matches_lockout_end"],
                "raw_coverage_beyond_derived": audit["summary"]["raw_coverage_beyond_derived"],
                "boundary_classification": audit["summary"]["boundary_classification"],
                "authoritative_rule": (
                    "the shadow bridge remains blocked because the current stop is best classified as a lockout-aligned derivation boundary, "
                    "not as missing raw data or a last-execution truncation"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hc_commercial_aerospace_hb_boundary_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
