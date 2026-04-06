from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129JCommercialAerospaceIJLatePreheatGovernanceTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V129JCommercialAerospaceIJLatePreheatGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v129i_commercial_aerospace_late_preheat_entry_mismatch_audit_v1.json"

    def analyze(self) -> V129JCommercialAerospaceIJLatePreheatGovernanceTriageReport:
        payload = json.loads(self.audit_path.read_text(encoding="utf-8"))
        mismatch_rate = float(payload["summary"]["late_preheat_full_mismatch_rate"])
        summary = {
            "acceptance_posture": "freeze_v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1",
            "late_preheat_full_mismatch_rate": mismatch_rate,
            "authoritative_status": (
                "retain_governance_rule_and_failure_cases"
                if mismatch_rate > 0
                else "no_mismatch_found"
            ),
            "authoritative_rule": "late-preheat supervision currently belongs in governance and failure-library review unless it proves replay-frontier improvement",
        }
        interpretation = [
            "V1.29J freezes how the full_pre supervision should be used after the late-preheat replay filter failed to improve the primary reference.",
            "The correct near-term role is governance: flag over-escalated late-preheat full entries and retain them as failure cases.",
        ]
        return V129JCommercialAerospaceIJLatePreheatGovernanceTriageReport(summary=summary, interpretation=interpretation)


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129JCommercialAerospaceIJLatePreheatGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129JCommercialAerospaceIJLatePreheatGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
