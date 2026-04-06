from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    authoritative_decision: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "authoritative_decision": self.authoritative_decision,
        }


class V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1.json"

    def analyze(self) -> V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        triage_rows = []
        for row in report["candidate_rows"]:
            if row["recommended_watch_status"] == "nearest_same_plane_watch":
                direction = "watch_as_second_same_plane_candidate_but_do_not_open_worker"
            elif row["recommended_watch_status"] == "historical_bridge_watch":
                direction = "retain_as_bridge_memory_only"
            else:
                direction = "no_worker_implication"
            triage_rows.append(
                {
                    "symbol": row["symbol"],
                    "recommended_watch_status": row["recommended_watch_status"],
                    "direction": direction,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130o_bk0808_military_civil_fusion_no_worker_watch_triage_v1",
            "nearest_same_plane_watch": report["summary"]["nearest_same_plane_watch"],
            "authoritative_status": "monitor_bk0808_emergence_candidates_without_unlocking_a_worker",
        }
        authoritative_decision = [
            "Keep the transfer program frozen.",
            "Treat 600118 as the nearest BK0808 second-same-plane watch candidate.",
            "Treat 600760 only as historical bridge memory.",
            "Do not open a BK0808 worker until v6 native same-plane support actually appears.",
        ]
        return V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            authoritative_decision=authoritative_decision,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130OBK0808MilitaryCivilFusionNoWorkerWatchTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130o_bk0808_military_civil_fusion_no_worker_watch_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
