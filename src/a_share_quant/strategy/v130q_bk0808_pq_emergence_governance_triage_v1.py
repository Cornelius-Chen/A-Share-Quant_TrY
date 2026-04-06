from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130QBK0808PQEmergenceGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    authoritative_decision: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "authoritative_decision": self.authoritative_decision,
        }


class V130QBK0808PQEmergenceGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130p_bk0808_second_symbol_emergence_trigger_protocol_v1.json"

    def analyze(self) -> V130QBK0808PQEmergenceGovernanceTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        triage_rows = []
        for row in report["trigger_rows"]:
            direction = (
                "reopen_candidate_only_after_real_v6_emergence"
                if row["reopen_candidate_if_emerged"]
                else "watch_only"
            )
            triage_rows.append(
                {
                    "symbol": row["symbol"],
                    "direction": direction,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130q_bk0808_pq_emergence_governance_triage_v1",
            "reopen_candidate_symbol": report["trigger_rows"][0]["symbol"] if report["trigger_rows"] else None,
            "authoritative_status": "monitor_600118_as_bk0808_emergence_trigger_but_keep_worker_frozen_until_real_same_plane_support_appears",
        }
        authoritative_decision = [
            "Keep BK0808 frozen.",
            "Treat 600118 as the decisive emergence watch name.",
            "Upgrade BK0808 only when 600118 gains actual v6 same-plane support while board strength remains acceptable.",
            "Do not treat timeline-native support alone as enough for reopening.",
        ]
        return V130QBK0808PQEmergenceGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            authoritative_decision=authoritative_decision,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130QBK0808PQEmergenceGovernanceTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130QBK0808PQEmergenceGovernanceTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130q_bk0808_pq_emergence_governance_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
