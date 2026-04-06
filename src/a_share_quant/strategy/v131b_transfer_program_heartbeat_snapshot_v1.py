from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131BTransferProgramHeartbeatSnapshotReport:
    summary: dict[str, Any]
    markdown_lines: list[str]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "markdown_lines": self.markdown_lines,
            "interpretation": self.interpretation,
        }


class V131BTransferProgramHeartbeatSnapshotAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.readiness_path = (
            repo_root / "reports" / "analysis" / "v130z_transfer_program_reopen_readiness_status_v1.json"
        )
        self.status_card_path = (
            repo_root / "reports" / "analysis" / "v131a_transfer_program_operational_status_card_v1.json"
        )
        self.output_md_path = (
            repo_root / "reports" / "analysis" / "v131b_transfer_program_heartbeat_snapshot_v1.md"
        )

    def analyze(self) -> V131BTransferProgramHeartbeatSnapshotReport:
        readiness = json.loads(self.readiness_path.read_text(encoding="utf-8"))
        status_card = json.loads(self.status_card_path.read_text(encoding="utf-8"))
        status_lookup = {row["status_key"]: row["status_value"] for row in status_card["status_rows"]}

        summary = {
            "acceptance_posture": "freeze_v131b_transfer_program_heartbeat_snapshot_v1",
            "program_status": status_lookup["program_status"],
            "rerun_required": readiness["summary"]["rerun_required"],
            "changed_artifact_count": readiness["summary"]["changed_artifact_count"],
            "nearest_candidate_sector_id": status_lookup["nearest_candidate_sector_id"],
            "decisive_watch_symbol": status_lookup["decisive_watch_symbol"],
            "next_action": status_lookup["next_action"],
            "authoritative_status": "heartbeat_snapshot_ready_for_daily_do_not_rerun_check",
        }
        markdown_lines = [
            "# Transfer Program Heartbeat",
            "",
            f"- Program status: `{status_lookup['program_status']}`",
            f"- Rerun required: `{readiness['summary']['rerun_required']}`",
            f"- Changed artifacts: `{readiness['summary']['changed_artifact_count']}`",
            f"- Nearest candidate: `{status_lookup['nearest_candidate_sector_id']}`",
            f"- Decisive watch symbol: `{status_lookup['decisive_watch_symbol']}`",
            f"- BK0808 current v6 symbol count: `{status_lookup['bk0808_current_v6_symbol_count']}`",
            f"- BK0808 same-plane symbol gap: `{status_lookup['bk0808_same_plane_symbol_gap']}`",
            f"- BK0808 bridge block: `{status_lookup['bk0808_bridge_block']}`",
            f"- Watch symbol near-surface days: `{status_lookup['watch_symbol_near_surface_days']}`",
            f"- Next action: `{status_lookup['next_action']}`",
        ]
        interpretation = [
            "V1.31B turns the frozen transfer governance bundle into a daily heartbeat snapshot.",
            "The purpose is not new inference but fast operational confirmation that the correct posture is still do-not-rerun under static data.",
        ]
        return V131BTransferProgramHeartbeatSnapshotReport(
            summary=summary,
            markdown_lines=markdown_lines,
            interpretation=interpretation,
        )

    def write_markdown(self, lines: list[str]) -> Path:
        self.output_md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return self.output_md_path


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131BTransferProgramHeartbeatSnapshotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V131BTransferProgramHeartbeatSnapshotAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131b_transfer_program_heartbeat_snapshot_v1",
        result=result,
    )
    analyzer.write_markdown(result.markdown_lines)


if __name__ == "__main__":
    main()
