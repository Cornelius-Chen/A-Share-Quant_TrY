from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130WTransferProgramVWGovernanceFreezeTriageReport:
    summary: dict[str, Any]
    authoritative_decision: list[str]
    next_posture: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "authoritative_decision": self.authoritative_decision,
            "next_posture": self.next_posture,
        }


class V130WTransferProgramVWGovernanceFreezeTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130v_transfer_program_governance_bundle_v1.json"

    def analyze(self) -> V130WTransferProgramVWGovernanceFreezeTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v130w_transfer_program_vw_governance_freeze_triage_v1",
            "closest_candidate_sector_id": report["summary"]["closest_candidate_sector_id"],
            "decisive_watch_symbol": report["summary"]["decisive_watch_symbol"],
            "authoritative_status": "stop_same_data_board_reanalysis_and_wait_for_new_local_support",
        }
        authoritative_decision = [
            "Keep the transfer program frozen.",
            "Treat the governance bundle as the current final monitoring surface under static data.",
            "Do not keep generating new board-transfer analytics off the same unchanged evidence.",
        ]
        next_posture = [
            "Reopen analysis only when new local v6 same-plane evidence appears.",
            "If BK0808 gets real 600118 same-plane support, rerun the reopen protocol immediately.",
            "Otherwise maintain watchlist monitoring only.",
        ]
        return V130WTransferProgramVWGovernanceFreezeTriageReport(
            summary=summary,
            authoritative_decision=authoritative_decision,
            next_posture=next_posture,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130WTransferProgramVWGovernanceFreezeTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130WTransferProgramVWGovernanceFreezeTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130w_transfer_program_vw_governance_freeze_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
