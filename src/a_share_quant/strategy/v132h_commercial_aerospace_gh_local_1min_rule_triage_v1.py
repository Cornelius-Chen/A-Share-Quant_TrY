from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132HCommercialAerospaceGHLocal1MinRuleTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132HCommercialAerospaceGHLocal1MinRuleTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1.json"
        )

    def analyze(self) -> V132HCommercialAerospaceGHLocal1MinRuleTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        if audit["summary"]["matched_count"] == audit["summary"]["registry_row_count"]:
            status = "retain_local_1min_tier_rule_candidates_as_governed_seed_rules_and_shift_next_to_broader_false_positive_audit"
        else:
            status = "keep_local_1min_tier_rule_candidates_as_draft_only"

        triage_rows = [
            {
                "component": "local_1min_tier_rule_candidates",
                "status": status,
                "rationale": "seed rules are worth keeping only if they preserve the frozen severe/reversal/mild ordering on the registry before any broader expansion",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "seed-rule coherence still does not authorize replay modification",
            },
        ]
        interpretation = [
            "V1.32H turns the first 1-minute seed-rule audit into a governance verdict.",
            "The next correct move is a broader false-positive audit over local minute sessions, not replay modification.",
        ]
        return V132HCommercialAerospaceGHLocal1MinRuleTriageReport(
            summary={
                "acceptance_posture": "freeze_v132h_commercial_aerospace_gh_local_1min_rule_triage_v1",
                "authoritative_status": status,
                "matched_count": audit["summary"]["matched_count"],
                "registry_row_count": audit["summary"]["registry_row_count"],
                "authoritative_rule": "the minute branch may keep 1min tier rules as governed seed rules once they preserve the frozen seed ordering, but broader false-positive auditing must come before any stronger claims",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132HCommercialAerospaceGHLocal1MinRuleTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132HCommercialAerospaceGHLocal1MinRuleTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132h_commercial_aerospace_gh_local_1min_rule_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
