from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131XCommercialAerospaceWXLocal5MinAmbiguousTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131XCommercialAerospaceWXLocal5MinAmbiguousTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1.json"
        )

    def analyze(self) -> V131XCommercialAerospaceWXLocal5MinAmbiguousTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        if summary["mild_override_watch_count"] == summary["flagged_non_override_case_count"]:
            status = "retain_all_flagged_ambiguous_hits_as_mild_override_watch_seeds"
        elif summary["mild_override_watch_count"] > 0:
            status = "retain_partial_mild_override_watch_seeds_and_keep_remaining_as_documented_false_positive_boundary"
        else:
            status = "keep_all_flagged_ambiguous_hits_as_documented_false_positive_boundary"

        triage_rows = [
            {
                "component": "flagged_ambiguous_5min_cases",
                "status": status,
                "rationale": "ambiguous hits should only be promoted when they resemble genuine mild override behavior rather than ordinary prototype leakage",
            },
            {
                "component": "local_5min_override_prototype",
                "status": "retain_governed_supervision",
                "rationale": "the broader prototype remains governance-only regardless of whether some ambiguous hits are retained as mild watch seeds",
            },
        ]
        interpretation = [
            "V1.31X turns the ambiguous-hit case audit into a narrow governance verdict.",
            "The decision here affects only the supervision seed library, not the lawful EOD primary replay.",
        ]
        return V131XCommercialAerospaceWXLocal5MinAmbiguousTriageReport(
            summary={
                "acceptance_posture": "freeze_v131x_commercial_aerospace_wx_local_5min_ambiguous_triage_v1",
                "authoritative_status": status,
                "flagged_non_override_case_count": summary["flagged_non_override_case_count"],
                "mild_override_watch_count": summary["mild_override_watch_count"],
                "documented_false_positive_count": summary["documented_false_positive_count"],
                "authoritative_rule": "ambiguous local 5min hits may expand the supervision seed library only when they look like mild override watches; otherwise they remain explicit false-positive boundaries",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131XCommercialAerospaceWXLocal5MinAmbiguousTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131XCommercialAerospaceWXLocal5MinAmbiguousTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131x_commercial_aerospace_wx_local_5min_ambiguous_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
