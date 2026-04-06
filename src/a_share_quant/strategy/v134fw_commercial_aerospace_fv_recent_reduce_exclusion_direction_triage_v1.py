from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1.json"
        )

    def analyze(self) -> V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_recent_reduce_residue_as_local_active_wave_exclusion_clue_and_keep_add_execution_blocked"
        )
        triage_rows = [
            {
                "component": "recent_reduce_residue_exclusion",
                "status": "retain_as_local_negative_clue",
                "rationale": "it excludes the only displaced active-wave candidate and none of the selected candidates",
            },
            {
                "component": "active_wave_daily_ranker",
                "status": "not_yet_authorized",
                "rationale": "the exclusion clue is still too small to be treated as a full ranking or execution authority layer",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "the branch now owns a local exclusion clue, not a complete add-selection engine",
            },
        ]
        interpretation = [
            "V1.34FW turns the first active-wave exclusion audit into the current governance verdict for the add frontier.",
            "The branch should retain recent-reduce residue as a local exclusion clue, but it should not mistake that for a complete daily ranker or execution-ready authority.",
        ]
        return V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fw_commercial_aerospace_fv_recent_reduce_exclusion_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "candidate_count": audit["summary"]["candidate_count"],
                "excluded_count": audit["summary"]["excluded_count"],
                "displaced_precision": audit["summary"]["displaced_precision"],
                "displaced_coverage": audit["summary"]["displaced_coverage"],
                "authoritative_rule": (
                    "recent reduce residue can now stay as the first active-wave exclusion clue, while broader promotion and execution remain blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fw_commercial_aerospace_fv_recent_reduce_exclusion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
