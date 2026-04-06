from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.bridge_path = repo_root / "reports" / "analysis" / "v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1.json"

    def analyze(self) -> V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageReport:
        bridge = json.loads(self.bridge_path.read_text(encoding="utf-8"))
        direction_rows = [
            {
                "direction": "600760_historical_bridge",
                "status": "retain_as_confirmation_memory_only",
                "reason": "The bridge is real enough to keep, but not clean enough to widen current control authority.",
            },
            {
                "direction": "bk0480_control_refresh",
                "status": "blocked",
                "reason": "Historical bridge formalization did not solve same-plane harmonization, so control refresh remains blocked.",
            },
            {
                "direction": "bk0480_replay_unlock",
                "status": "blocked",
                "reason": "Replay still cannot be unlocked from confirmation language plus a historical bridge alone.",
            },
            {
                "direction": "next_primary_direction",
                "status": "freeze_bk0480_and_shift_attention_to_shadow_next_board_preparation",
                "reason": "BK0480 has now exhausted the lawful local expansion and bridge-formalization path without reaching replay readiness.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v130f_bk0480_aerospace_aviation_ef_historical_bridge_direction_triage_v1",
            "board_name": bridge["summary"]["board_name"],
            "sector_id": bridge["summary"]["sector_id"],
            "bridge_strength": bridge["summary"]["bridge_strength"],
            "harmonization_status": bridge["summary"]["harmonization_status"],
            "authoritative_status": "freeze_bk0480_after_role_surface_v2_plus_historical_bridge_formalization_and_do_not_pretend_replay_readiness",
            "authoritative_rule": "bk0480_should_now_be_treated_as_a_transfer_preparation_case_that_stopped_at_harmonization_block",
        }
        interpretation = [
            "V1.30F closes the BK0480 local loop after historical bridge formalization.",
            "The board taught a useful portability lesson, but it did not mature into a replay-capable local system.",
        ]
        return V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130f_bk0480_aerospace_aviation_ef_historical_bridge_direction_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
