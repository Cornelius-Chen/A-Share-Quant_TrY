from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132BCommercialAerospaceABMinuteLabelDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132BCommercialAerospaceABMinuteLabelDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_report_path = (
            repo_root / "reports" / "analysis" / "v132a_commercial_aerospace_minute_tiered_label_specification_v1.json"
        )

    def analyze(self) -> V132BCommercialAerospaceABMinuteLabelDirectionTriageReport:
        spec = json.loads(self.spec_report_path.read_text(encoding="utf-8"))
        status = "freeze_minute_tiered_label_specification_and_shift_next_to_local_1min_seed_window_extraction"
        triage_rows = [
            {
                "component": "minute_tiered_label_specification",
                "status": status,
                "rationale": "the branch is ready to move from 5-minute governed supervision into explicit 1-minute seed-window extraction under tiered labels",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "tier specification still belongs to supervision and does not authorize replay contamination",
            },
        ]
        interpretation = [
            "V1.32B freezes the minute-tier vocabulary as the next canonical step for the commercial-aerospace intraday branch.",
            "The next task is local 1-minute seed-window extraction, not replay modification.",
        ]
        return V132BCommercialAerospaceABMinuteLabelDirectionTriageReport(
            summary={
                "acceptance_posture": "freeze_v132b_commercial_aerospace_ab_minute_label_direction_triage_v1",
                "authoritative_status": status,
                "registry_row_count": spec["summary"]["registry_row_count"],
                "severity_tier_count": spec["summary"]["severity_tier_count"],
                "authoritative_rule": "the commercial-aerospace minute branch should next extract local 1-minute seed windows under the frozen severe/reversal/mild supervision vocabulary",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132BCommercialAerospaceABMinuteLabelDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132BCommercialAerospaceABMinuteLabelDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132b_commercial_aerospace_ab_minute_label_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
