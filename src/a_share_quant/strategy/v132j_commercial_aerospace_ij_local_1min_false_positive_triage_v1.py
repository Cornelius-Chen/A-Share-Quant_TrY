from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1.json"
        )

    def analyze(self) -> V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        if summary["clean_control_flagged_count"] == 0:
            status = "retain_local_1min_tier_rule_candidates_as_bounded_governed_supervision_and_shift_next_to_minute_session_expansion_audit"
        else:
            status = "keep_local_1min_tier_rule_candidates_seed_only"

        triage_rows = [
            {
                "component": "local_1min_tier_rule_candidates",
                "status": status,
                "rationale": "broader expansion is acceptable only if the first false-positive audit stays off clean controls",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "even a bounded false-positive profile does not authorize replay contamination",
            },
        ]
        interpretation = [
            "V1.32J turns the first broader 1-minute false-positive audit into a governance verdict.",
            "If clean controls stay untouched, the rule candidates can graduate from seed-only to bounded governed supervision; otherwise they stay seed-only.",
        ]
        return V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageReport(
            summary={
                "acceptance_posture": "freeze_v132j_commercial_aerospace_ij_local_1min_false_positive_triage_v1",
                "authoritative_status": status,
                "seed_match_count": summary["seed_match_count"],
                "seed_row_count": summary["seed_row_count"],
                "non_seed_flagged_count": summary["non_seed_flagged_count"],
                "clean_control_flagged_count": summary["clean_control_flagged_count"],
                "authoritative_rule": "the first local 1min rules can advance beyond seed-only status only when the broader false-positive surface remains bounded away from clean controls",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132j_commercial_aerospace_ij_local_1min_false_positive_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
