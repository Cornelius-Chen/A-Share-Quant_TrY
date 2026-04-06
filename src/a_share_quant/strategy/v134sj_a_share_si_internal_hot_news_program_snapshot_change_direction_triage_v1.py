from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134si_a_share_internal_hot_news_program_snapshot_change_signal_audit_v1 import (
    V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Report:
        report = V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "change_row_count": report.summary["change_row_count"],
            "top_risk_change_state": report.summary["top_risk_change_state"],
            "top_opportunity_change_state": report.summary["top_opportunity_change_state"],
            "authoritative_status": "continue_serving_snapshot_change_signal_for_polling_or_alert_logic",
        }
        triage_rows = [
            {
                "component": "stable_state",
                "direction": "treat_stable_as_no_new_top-level_rotation_even_if_background_feeds_still_exist",
            },
            {
                "component": "entity_change_state",
                "direction": "treat_top_entity_changed_as_a_higher-priority_rotation_signal_than_simple_score_drift",
            },
            {
                "component": "score_shift_state",
                "direction": "treat_major_or_minor_score_shift_as_signal_intensity_change_without_assuming_entity_rotation",
            },
        ]
        interpretation = [
            "The snapshot change signal is a thin alert layer above the snapshot, not a new semantic source.",
            "It is most useful when the consumer polls frequently and only wants to react to top-level changes.",
        ]
        return V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sj_a_share_si_internal_hot_news_program_snapshot_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
