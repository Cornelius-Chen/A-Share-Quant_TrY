from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131TCommercialAerospaceSTLocal5MinOverrideTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131TCommercialAerospaceSTLocal5MinOverrideTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131s_commercial_aerospace_local_5min_override_prototype_audit_v1.json"
        )

    def analyze(self) -> V131TCommercialAerospaceSTLocal5MinOverrideTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        if (
            summary["override_positive_hit_count"] == summary["override_positive_total"]
            and summary["reversal_watch_hit_count"] == summary["reversal_watch_total"]
            and summary["clean_control_hit_count"] == 0
        ):
            authoritative_status = (
                "retain_commercial_aerospace_local_5min_override_prototype_as_governed_supervision"
            )
        else:
            authoritative_status = "keep_commercial_aerospace_local_5min_override_prototype_explanatory_only"

        triage_rows = [
            {
                "component": "local_5min_collapse_override_prototype",
                "status": authoritative_status,
                "rationale": "the prototype is only valuable if it cleanly covers retained severe cases while staying off clean controls",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the new 5min prototype is supervision/governance only and does not directly modify the current primary replay stack",
            },
        ]
        result_summary = {
            "acceptance_posture": "freeze_v131t_commercial_aerospace_st_local_5min_override_triage_v1",
            "authoritative_status": authoritative_status,
            "override_positive_hit_count": summary["override_positive_hit_count"],
            "override_positive_total": summary["override_positive_total"],
            "reversal_watch_hit_count": summary["reversal_watch_hit_count"],
            "reversal_watch_total": summary["reversal_watch_total"],
            "clean_control_hit_count": summary["clean_control_hit_count"],
            "clean_control_total": summary["clean_control_total"],
            "authoritative_rule": "the first local 5min prototype is retained only as a governance-bound supervision layer unless later minute-level work proves it lawful and replay-worthy",
        }
        interpretation = [
            "V1.31T turns the narrow local 5-minute prototype into a governance verdict.",
            "The correct current posture is supervision-first: the prototype can guide future minute-level work without being allowed to contaminate the lawful EOD replay stack.",
        ]
        return V131TCommercialAerospaceSTLocal5MinOverrideTriageReport(
            summary=result_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131TCommercialAerospaceSTLocal5MinOverrideTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131TCommercialAerospaceSTLocal5MinOverrideTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131t_commercial_aerospace_st_local_5min_override_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
