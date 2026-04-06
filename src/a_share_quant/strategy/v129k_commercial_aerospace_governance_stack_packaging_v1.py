from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129KCommercialAerospaceGovernanceStackPackagingReport:
    summary: dict[str, Any]
    governance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "governance_rows": self.governance_rows,
            "interpretation": self.interpretation,
        }


class V129KCommercialAerospaceGovernanceStackPackagingAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.timechain_path = repo_root / "reports" / "analysis" / "v128q_commercial_aerospace_opq_timechain_governance_triage_v1.json"
        self.failure_path = repo_root / "reports" / "analysis" / "v128t_commercial_aerospace_failure_library_triage_v1.json"
        self.intraday_path = repo_root / "reports" / "analysis" / "v128v_commercial_aerospace_intraday_collapse_override_triage_v1.json"
        self.state_machine_path = repo_root / "reports" / "analysis" / "v128x_commercial_aerospace_phase_state_machine_triage_v1.json"
        self.walk_forward_path = repo_root / "reports" / "analysis" / "v129f_commercial_aerospace_def_walk_forward_direction_triage_v1.json"
        self.late_preheat_path = repo_root / "reports" / "analysis" / "v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1.json"

    def analyze(self) -> V129KCommercialAerospaceGovernanceStackPackagingReport:
        timechain = json.loads(self.timechain_path.read_text(encoding="utf-8"))
        failure = json.loads(self.failure_path.read_text(encoding="utf-8"))
        intraday = json.loads(self.intraday_path.read_text(encoding="utf-8"))
        state_machine = json.loads(self.state_machine_path.read_text(encoding="utf-8"))
        walk_forward = json.loads(self.walk_forward_path.read_text(encoding="utf-8"))
        late_preheat = json.loads(self.late_preheat_path.read_text(encoding="utf-8"))

        governance_rows = [
            {
                "layer": "timechain_transparency",
                "status": "retained_governance",
                "rule": "all commercial-aerospace replay audits should show signal_date, execution_date, and pre_open_event_status together",
                "source_status": timechain["summary"]["authoritative_status"],
            },
            {
                "layer": "pre_open_decisive_event_veto",
                "status": "retained_governance",
                "rule": "decisive adverse events are checked in the pre-open window, but they do not alter replay economics until a lawful trigger population exists",
                "source_status": timechain["summary"]["authoritative_status"],
            },
            {
                "layer": "failure_library",
                "status": "retained_supervision",
                "rule": "lawful-but-suspicious trades should be preserved as failure cases even when they cannot yet translate into replay-facing actions",
                "source_status": failure["summary"]["next_direction"],
            },
            {
                "layer": "intraday_collapse_override",
                "status": "supervision_only",
                "rule": "intraday collapse override remains a retained supervision object and must not be mixed into current EOD lawful replay",
                "source_status": intraday["summary"]["authoritative_status"],
            },
            {
                "layer": "phase_state_machine",
                "status": "authoritative_supervision_surface",
                "rule": "commercial aerospace must be represented as probe / full_pre / full / de_risk rather than a binary probe/full ladder",
                "source_status": state_machine["summary"]["authoritative_status"],
            },
            {
                "layer": "phase_specific_walk_forward",
                "status": "partial_support_only",
                "rule": "full_pre may continue as phase-specific walk-forward supervision; full remains phase-contextual until thicker lawful support exists",
                "source_status": walk_forward["summary"]["authoritative_status"],
            },
            {
                "layer": "late_preheat_mismatch_governance",
                "status": "retained_governance_rule",
                "rule": "late-preheat full entries that do not align with the full_pre supervision state must be tracked as governance failures before any replay-side expansion",
                "source_status": late_preheat["summary"]["authoritative_status"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129k_commercial_aerospace_governance_stack_packaging_v1",
            "governance_layer_count": len(governance_rows),
            "current_primary_variant": "tail_weakdrift_full",
            "authoritative_output": "commercial_aerospace_governance_stack_frozen_for_state_management_and_portability_work",
        }
        interpretation = [
            "V1.29K packages the commercial-aerospace governance stack after replay-side micro-tuning was stopped.",
            "The output is not a new alpha family; it is the authoritative supervision/governance surface that should accompany the frozen primary replay.",
        ]
        return V129KCommercialAerospaceGovernanceStackPackagingReport(
            summary=summary,
            governance_rows=governance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129KCommercialAerospaceGovernanceStackPackagingReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129KCommercialAerospaceGovernanceStackPackagingAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129k_commercial_aerospace_governance_stack_packaging_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
