from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.seed_report_path = (
            repo_root / "reports" / "analysis" / "v132c_commercial_aerospace_local_1min_seed_window_extraction_v1.json"
        )

    def analyze(self) -> V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageReport:
        seed = json.loads(self.seed_report_path.read_text(encoding="utf-8"))
        status = "freeze_local_1min_seed_window_table_and_shift_next_to_minute_pattern_envelope_audit"
        triage_rows = [
            {
                "component": "local_1min_seed_windows",
                "status": status,
                "rationale": "the branch now has a canonical first-hour 1-minute table for all retained supervision seeds and can move to minute-pattern envelope work",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the new 1-minute seed windows remain supervision-only and do not authorize replay contamination",
            },
        ]
        interpretation = [
            "V1.32D turns the extracted local 1-minute seed windows into the next minute-branch direction.",
            "The immediate next step is envelope/pattern work over the frozen seed windows, not direct replay modification.",
        ]
        return V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageReport(
            summary={
                "acceptance_posture": "freeze_v132d_commercial_aerospace_cd_local_1min_seed_direction_triage_v1",
                "authoritative_status": status,
                "registry_session_count": seed["summary"]["registry_session_count"],
                "seed_window_row_count": seed["summary"]["seed_window_row_count"],
                "authoritative_rule": "the next minute-branch task is to characterize 1-minute pattern envelopes over the frozen seed windows, not to modify replay",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132d_commercial_aerospace_cd_local_1min_seed_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
