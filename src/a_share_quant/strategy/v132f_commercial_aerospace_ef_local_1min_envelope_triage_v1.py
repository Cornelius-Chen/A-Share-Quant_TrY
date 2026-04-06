from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132FCommercialAerospaceEFLocal1MinEnvelopeTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132FCommercialAerospaceEFLocal1MinEnvelopeTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.envelope_report_path = (
            repo_root / "reports" / "analysis" / "v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1.json"
        )

    def analyze(self) -> V132FCommercialAerospaceEFLocal1MinEnvelopeTriageReport:
        envelope = json.loads(self.envelope_report_path.read_text(encoding="utf-8"))
        status = "freeze_local_1min_pattern_envelopes_and_shift_next_to_rule_candidate_extraction"
        triage_rows = [
            {
                "component": "local_1min_pattern_envelopes",
                "status": status,
                "rationale": "the minute branch now has explicit first-hour envelope summaries and can move next toward candidate rule extraction over the seed windows",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "pattern envelopes remain minute-governance artifacts and do not authorize replay modification",
            },
        ]
        interpretation = [
            "V1.32F turns the first-hour 1-minute envelopes into the next direction for the commercial-aerospace minute branch.",
            "The next task is rule-candidate extraction from the frozen seed envelopes, not replay modification.",
        ]
        return V132FCommercialAerospaceEFLocal1MinEnvelopeTriageReport(
            summary={
                "acceptance_posture": "freeze_v132f_commercial_aerospace_ef_local_1min_envelope_triage_v1",
                "authoritative_status": status,
                "session_count": envelope["summary"]["session_count"],
                "severity_tier_count": envelope["summary"]["severity_tier_count"],
                "authoritative_rule": "the commercial-aerospace minute branch should now extract 1min rule candidates from frozen tier envelopes rather than continuing ad hoc case discussion",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132FCommercialAerospaceEFLocal1MinEnvelopeTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132FCommercialAerospaceEFLocal1MinEnvelopeTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132f_commercial_aerospace_ef_local_1min_envelope_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
