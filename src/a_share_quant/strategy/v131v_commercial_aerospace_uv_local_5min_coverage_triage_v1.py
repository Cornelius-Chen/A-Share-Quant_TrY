from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131VCommercialAerospaceUVLocal5MinCoverageTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131VCommercialAerospaceUVLocal5MinCoverageTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.coverage_report_path = (
            repo_root / "reports" / "analysis" / "v131u_commercial_aerospace_local_5min_override_coverage_audit_v1.json"
        )

    def analyze(self) -> V131VCommercialAerospaceUVLocal5MinCoverageTriageReport:
        coverage = json.loads(self.coverage_report_path.read_text(encoding="utf-8"))
        summary = coverage["summary"]

        ambiguous_ok = summary["ambiguous_hit_rate"] <= 0.15
        clean_ok = summary["clean_control_hit_count"] == 0
        non_override_flagged = summary["non_override_flagged_count"]

        if clean_ok and ambiguous_ok:
            status = "retain_local_5min_override_prototype_as_narrow_governed_supervision_with_false_positive_bounds_documented"
        else:
            status = "keep_local_5min_override_prototype_but_do_not_expand_without_rule_revision"

        triage_rows = [
            {
                "component": "local_5min_override_prototype",
                "status": status,
                "rationale": "the prototype should remain governance-only and acceptable only if it avoids clean controls and keeps residual false positives confined to ambiguous executions",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "coverage auditing still does not authorize replay contamination; the EOD primary stays unchanged",
            },
        ]
        interpretation = [
            "V1.31V turns the broader 5-minute coverage audit into a governance verdict.",
            "The retained posture remains narrow: this is a bounded supervision object, not a replay-facing intraday execution rule.",
        ]
        return V131VCommercialAerospaceUVLocal5MinCoverageTriageReport(
            summary={
                "acceptance_posture": "freeze_v131v_commercial_aerospace_uv_local_5min_coverage_triage_v1",
                "authoritative_status": status,
                "non_override_flagged_count": non_override_flagged,
                "ambiguous_hit_rate": summary["ambiguous_hit_rate"],
                "clean_control_hit_count": summary["clean_control_hit_count"],
                "authoritative_rule": "expand the governed 5min prototype only as a documented supervision layer with explicit false-positive bounds, never as a silent replay modifier",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131VCommercialAerospaceUVLocal5MinCoverageTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131VCommercialAerospaceUVLocal5MinCoverageTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131v_commercial_aerospace_uv_local_5min_coverage_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
