from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130UBK0808TUEmergenceStateGovernanceTriageReport:
    summary: dict[str, Any]
    authoritative_decision: list[str]
    state_counts: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "authoritative_decision": self.authoritative_decision,
            "state_counts": self.state_counts,
        }


class V130UBK0808TUEmergenceStateGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130t_bk0808_emergence_watch_state_machine_v1.json"

    def analyze(self) -> V130UBK0808TUEmergenceStateGovernanceTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        state_counts: dict[str, int] = {}
        for row in report["state_rows"]:
            state_counts[row["watch_state"]] = state_counts.get(row["watch_state"], 0) + 1

        summary = {
            "acceptance_posture": "freeze_v130u_bk0808_tu_emergence_state_governance_triage_v1",
            "symbol": report["summary"]["symbol"],
            "authoritative_status": "retain_bk0808_watch_state_machine_as_governance_only_and_keep_worker_frozen",
        }
        authoritative_decision = [
            "Keep BK0808 frozen.",
            "Retain the 600118 watch state machine as governance infrastructure.",
            "Use near-surface watch as an early warning state only; do not reinterpret it as replay authority.",
        ]
        return V130UBK0808TUEmergenceStateGovernanceTriageReport(
            summary=summary,
            authoritative_decision=authoritative_decision,
            state_counts=state_counts,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130UBK0808TUEmergenceStateGovernanceTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130UBK0808TUEmergenceStateGovernanceTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130u_bk0808_tu_emergence_state_governance_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
