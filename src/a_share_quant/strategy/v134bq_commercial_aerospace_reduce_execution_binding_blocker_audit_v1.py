from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Report:
    summary: dict[str, Any]
    blocker_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "blocker_rows": self.blocker_rows,
            "interpretation": self.interpretation,
        }


class V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.unblock_protocol_path = (
            repo_root / "reports" / "analysis" / "v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1.json"
        )
        self.build_protocol_path = (
            repo_root / "reports" / "analysis" / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        )
        self.build_triage_path = (
            repo_root / "reports" / "analysis" / "v133n_commercial_aerospace_intraday_execution_build_triage_v1.json"
        )
        self.reduce_closure_path = (
            repo_root / "reports" / "analysis" / "v134bo_commercial_aerospace_reduce_closure_governance_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reduce_execution_binding_blocker_audit_v1.csv"
        )

    def analyze(self) -> V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Report:
        unblock = json.loads(self.unblock_protocol_path.read_text(encoding="utf-8"))
        build = json.loads(self.build_protocol_path.read_text(encoding="utf-8"))
        triage = json.loads(self.build_triage_path.read_text(encoding="utf-8"))
        closure = json.loads(self.reduce_closure_path.read_text(encoding="utf-8"))

        blocker_rows = [
            {
                "blocker_order": 1,
                "blocker_name": "point_in_time_intraday_visibility",
                "status": "still_blocked",
                "affects_stage": "intraday_sell_ladder",
                "why_it_matters": "without minute-lawful visibility, sell ladder triggers cannot be execution-bound without leak risk",
                "required_for": "sell-side binding",
                "source": "v133c / v133m / v133n",
            },
            {
                "blocker_order": 2,
                "blocker_name": "intraday_execution_simulation_surface",
                "status": "still_blocked",
                "affects_stage": "intraday_sell_ladder_and_board_gate",
                "why_it_matters": "board gate and sell ladder cannot be tested as a unified intraday action path without a deterministic fill model",
                "required_for": "sell-plus-board binding",
                "source": "v133c / v133m",
            },
            {
                "blocker_order": 3,
                "blocker_name": "separate_intraday_replay_lane",
                "status": "still_blocked",
                "affects_stage": "all_reduce_closure_stages",
                "why_it_matters": "without a separate lane, sell, lockout, unlock, and reentry cannot be bound together without contaminating the frozen EOD primary",
                "required_for": "full_reduce_binding",
                "source": "v133c / v133m / v134bo",
            },
            {
                "blocker_order": 4,
                "blocker_name": "reentry_execution_surface",
                "status": "not_started",
                "affects_stage": "seed_reentry_ladder",
                "why_it_matters": "reentry timing supervision exists, but no lawful simulator or fill policy exists for rebuild actions",
                "required_for": "reentry binding",
                "source": "v134bc / v134bo",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(blocker_rows[0].keys()))
            writer.writeheader()
            writer.writerows(blocker_rows)

        summary = {
            "acceptance_posture": "freeze_v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1",
            "blocker_count": len(blocker_rows),
            "sell_side_binding_blocker_count": 2,
            "full_reduce_binding_blocker_count": len(blocker_rows),
            "consensus_guardrail_count": len(triage["consensus_rows"]),
            "closure_stage_count": closure["summary"]["closure_stage_count"],
            "blocker_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_execution_binding_blockers_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BQ stops speaking about execution binding abstractly and names the concrete missing surfaces.",
            "The branch can now separate what blocks sell-side binding from what blocks full reduce closure binding across sell, board gate, and reentry.",
        ]
        return V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Report(
            summary=summary,
            blocker_rows=blocker_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BQCommercialAerospaceReduceExecutionBindingBlockerAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
