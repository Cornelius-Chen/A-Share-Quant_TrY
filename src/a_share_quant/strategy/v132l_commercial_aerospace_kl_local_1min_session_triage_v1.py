from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132LCommercialAerospaceKLLocal1MinSessionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132LCommercialAerospaceKLLocal1MinSessionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v132k_commercial_aerospace_local_1min_session_expansion_audit_v1.json"
        )

    def analyze(self) -> V132LCommercialAerospaceKLLocal1MinSessionTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        if summary["max_symbol_hit_rate"] <= 0.2:
            status = "retain_local_1min_rules_as_sparse_bounded_governed_supervision"
        else:
            status = "keep_local_1min_rules_governed_but_treat_expansion_surface_as_too_wide"

        triage_rows = [
            {
                "component": "local_1min_rule_candidates",
                "status": status,
                "rationale": "the broader session surface should remain sparse enough to keep the minute rules interpretable and governed",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "session expansion auditing still belongs to supervision and does not authorize replay modification",
            },
        ]
        interpretation = [
            "V1.32L turns the broader local-session expansion audit into a governance verdict.",
            "The relevant question is no longer seed coherence, but whether the minute rules stay sparse enough on the retained-symbol session surface to remain interpretable.",
        ]
        return V132LCommercialAerospaceKLLocal1MinSessionTriageReport(
            summary={
                "acceptance_posture": "freeze_v132l_commercial_aerospace_kl_local_1min_session_triage_v1",
                "authoritative_status": status,
                "expanded_session_count": summary["expanded_session_count"],
                "expanded_hit_count": summary["expanded_hit_count"],
                "max_symbol_hit_rate": summary["max_symbol_hit_rate"],
                "authoritative_rule": "the commercial-aerospace minute branch may keep expanding only while the local 1min rules remain sparse and bounded on the broader retained-symbol session surface",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132LCommercialAerospaceKLLocal1MinSessionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132LCommercialAerospaceKLLocal1MinSessionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132l_commercial_aerospace_kl_local_1min_session_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
