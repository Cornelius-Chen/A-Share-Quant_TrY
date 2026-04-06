from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Report:
    summary: dict[str, Any]
    opening_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "opening_rows": self.opening_rows,
            "interpretation": self.interpretation,
        }


class V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_status_path = analysis_dir / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        self.add_status_path = analysis_dir / "v134go_commercial_aerospace_gn_add_completion_direction_triage_v1.json"
        self.build_protocol_path = analysis_dir / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_shadow_replay_lane_opening_v1.csv"
        )

    def analyze(self) -> V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Report:
        reduce_status = json.loads(self.reduce_status_path.read_text(encoding="utf-8"))
        add_status = json.loads(self.add_status_path.read_text(encoding="utf-8"))
        build_protocol = json.loads(self.build_protocol_path.read_text(encoding="utf-8"))

        opening_rows = [
            {
                "opening_stage": "frontier_scope",
                "status": "opened_protocol_only",
                "detail": "The new frontier is a unified intraday shadow replay lane, but only at protocol and supervision-binding scope.",
            },
            {
                "opening_stage": "reduce_branch",
                "status": "read_only_frozen_input",
                "detail": reduce_status["summary"]["reduce_handoff_status"],
            },
            {
                "opening_stage": "add_branch",
                "status": "read_only_frozen_supervision_input",
                "detail": add_status["summary"]["authoritative_status"],
            },
            {
                "opening_stage": "first_module",
                "status": "reentry_unlock_bridge_first",
                "detail": "The lane should first bind reentry/unlock supervision between frozen reduce and frozen add supervision before any broader intraday execution claims.",
            },
            {
                "opening_stage": "execution_authority",
                "status": "still_blocked",
                "detail": "The lane stays read-only and shadow-only; it does not inherit execution authority from reduce or promote add into execution.",
            },
            {
                "opening_stage": "build_order",
                "status": "reuse_existing_intraday_protocol",
                "detail": (
                    f"Reuse V1.33M sequencing: {build_protocol['sequencing_rows'][0]['phase']} -> "
                    f"{build_protocol['sequencing_rows'][1]['phase']} -> {build_protocol['sequencing_rows'][2]['phase']}"
                ),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(opening_rows[0].keys()))
            writer.writeheader()
            writer.writerows(opening_rows)

        summary = {
            "acceptance_posture": "open_v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1",
            "frontier_name": "intraday_shadow_replay_lane",
            "frontier_state": "opened_protocol_only",
            "input_branch_count": 2,
            "first_module": "reentry_unlock_shadow_bridge",
            "execution_authority": "still_blocked",
            "opening_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_shadow_replay_lane_opening_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34GP opens the next frontier after reduce and add both reached supervision stoplines.",
            "The new frontier is not another local alpha branch. It is a unifying shadow replay lane that treats frozen reduce and frozen add as read-only inputs and starts with reentry/unlock bridging.",
        ]
        return V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Report(
            summary=summary,
            opening_rows=opening_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
