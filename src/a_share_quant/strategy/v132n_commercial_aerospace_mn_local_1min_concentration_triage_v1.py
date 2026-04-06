from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132NCommercialAerospaceMNLocal1MinConcentrationTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132m_commercial_aerospace_local_1min_hit_concentration_audit_v1.json"
        )

    def analyze(self) -> V132NCommercialAerospaceMNLocal1MinConcentrationTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        if summary["main_window_hit_share"] >= 0.4 and summary["top_regime_semantic"] in {
            "risk_off_deterioration",
            "weak_drift_chop",
        }:
            status = "retain_local_1min_rules_as_window_aligned_bounded_governed_supervision"
        else:
            status = "retain_local_1min_rules_but_mark_temporal_alignment_as_inconclusive"

        triage_rows = [
            {
                "component": "local_1min_rule_candidates",
                "status": status,
                "rationale": "temporal concentration in the board's main drawdown window and risk-oriented regimes strengthens the case that the minute rules express real downside semantics rather than generic weakness",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "even aligned minute governance remains outside direct replay execution",
            },
        ]
        interpretation = [
            "V1.32N converts the temporal concentration audit into a governance verdict.",
            "The minute branch is stronger when the broader hit surface clusters around known risk windows and risk-oriented regimes rather than spreading uniformly over time.",
        ]
        return V132NCommercialAerospaceMNLocal1MinConcentrationTriageReport(
            summary={
                "acceptance_posture": "freeze_v132n_commercial_aerospace_mn_local_1min_concentration_triage_v1",
                "authoritative_status": status,
                "expanded_hit_count": summary["expanded_hit_count"],
                "main_window_hit_share": summary["main_window_hit_share"],
                "top_regime_semantic": summary["top_regime_semantic"],
                "authoritative_rule": "the local 1min branch gains credibility when its broader hit surface is temporally aligned with the board's main risk windows and downside-oriented structure regimes",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132NCommercialAerospaceMNLocal1MinConcentrationTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132n_commercial_aerospace_mn_local_1min_concentration_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
