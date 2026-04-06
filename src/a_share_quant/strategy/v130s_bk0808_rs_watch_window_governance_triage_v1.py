from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130SBK0808RSWatchWindowGovernanceTriageReport:
    summary: dict[str, Any]
    authoritative_decision: list[str]
    watch_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "authoritative_decision": self.authoritative_decision,
            "watch_rows": self.watch_rows,
        }


class V130SBK0808RSWatchWindowGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130r_bk0808_600118_near_surface_watch_window_audit_v1.json"

    def analyze(self) -> V130SBK0808RSWatchWindowGovernanceTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        active_rows = [row for row in report["watch_rows"] if row["near_surface_watch_active"]]
        summary = {
            "acceptance_posture": "freeze_v130s_bk0808_rs_watch_window_governance_triage_v1",
            "near_surface_watch_day_count": report["summary"]["near_surface_watch_day_count"],
            "authoritative_status": "retain_bk0808_watch_windows_for_governance_but_keep_worker_frozen",
        }
        authoritative_decision = [
            "Keep BK0808 frozen.",
            "Retain the 600118 near-surface watch windows as governance evidence.",
            "Do not convert near-surface windows into replay authority before real v6 same-plane support exists.",
        ]
        return V130SBK0808RSWatchWindowGovernanceTriageReport(
            summary=summary,
            authoritative_decision=authoritative_decision,
            watch_rows=active_rows,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130SBK0808RSWatchWindowGovernanceTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130SBK0808RSWatchWindowGovernanceTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130s_bk0808_rs_watch_window_governance_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
