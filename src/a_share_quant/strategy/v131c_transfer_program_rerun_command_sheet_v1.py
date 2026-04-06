from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RERUN_CHAIN_COMMANDS = {
    "v130g_to_v130w": [
        "python scripts/run_v130g_transfer_program_same_plane_support_freeze_v1.py",
        "python scripts/run_v130h_transfer_program_gh_same_plane_freeze_triage_v1.py",
        "python scripts/run_v130i_transfer_program_reopen_trigger_protocol_v1.py",
        "python scripts/run_v130j_transfer_program_ij_reopen_governance_triage_v1.py",
        "python scripts/run_v130k_transfer_program_watch_monitor_snapshot_v1.py",
        "python scripts/run_v130l_transfer_program_gap_closure_scenarios_v1.py",
        "python scripts/run_v130m_transfer_program_kl_gap_closure_triage_v1.py",
        "python scripts/run_v130v_transfer_program_governance_bundle_v1.py",
        "python scripts/run_v130w_transfer_program_vw_governance_freeze_triage_v1.py",
        "python scripts/run_v130x_transfer_program_change_detection_protocol_v1.py",
        "python scripts/run_v130y_transfer_program_xy_change_gate_triage_v1.py",
        "python scripts/run_v130z_transfer_program_reopen_readiness_status_v1.py",
        "python scripts/run_v131a_transfer_program_operational_status_card_v1.py",
        "python scripts/run_v131b_transfer_program_heartbeat_snapshot_v1.py",
    ],
    "v129y_to_v130w": [
        "python scripts/run_v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1.py",
        "python scripts/run_v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1.py",
        "python scripts/run_v130a_bk0480_aerospace_aviation_role_surface_refresh_v2.py",
        "python scripts/run_v130b_bk0480_aerospace_aviation_ab_role_surface_direction_triage_v1.py",
        "python scripts/run_v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1.py",
        "python scripts/run_v130d_bk0480_aerospace_aviation_cd_harmonization_triage_v1.py",
        "python scripts/run_v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1.py",
        "python scripts/run_v130f_bk0480_aerospace_aviation_ef_historical_bridge_direction_triage_v1.py",
    ],
    "v130n_to_v130w": [
        "python scripts/run_v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1.py",
        "python scripts/run_v130o_bk0808_military_civil_fusion_no_worker_watch_triage_v1.py",
        "python scripts/run_v130p_bk0808_second_symbol_emergence_trigger_protocol_v1.py",
        "python scripts/run_v130q_bk0808_pq_emergence_governance_triage_v1.py",
        "python scripts/run_v130r_bk0808_600118_near_surface_watch_window_audit_v1.py",
        "python scripts/run_v130s_bk0808_rs_watch_window_governance_triage_v1.py",
        "python scripts/run_v130t_bk0808_emergence_watch_state_machine_v1.py",
        "python scripts/run_v130u_bk0808_tu_emergence_state_governance_triage_v1.py",
        "python scripts/run_v130v_transfer_program_governance_bundle_v1.py",
        "python scripts/run_v130w_transfer_program_vw_governance_freeze_triage_v1.py",
        "python scripts/run_v130x_transfer_program_change_detection_protocol_v1.py",
        "python scripts/run_v130y_transfer_program_xy_change_gate_triage_v1.py",
        "python scripts/run_v130z_transfer_program_reopen_readiness_status_v1.py",
        "python scripts/run_v131a_transfer_program_operational_status_card_v1.py",
        "python scripts/run_v131b_transfer_program_heartbeat_snapshot_v1.py",
    ],
}


@dataclass(slots=True)
class V131CTransferProgramRerunCommandSheetReport:
    summary: dict[str, Any]
    chain_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "chain_rows": self.chain_rows,
            "interpretation": self.interpretation,
        }


class V131CTransferProgramRerunCommandSheetAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = repo_root / "reports" / "analysis" / "v130x_transfer_program_change_detection_protocol_v1.json"
        self.output_md_path = repo_root / "reports" / "analysis" / "v131c_transfer_program_rerun_command_sheet_v1.md"

    def analyze(self) -> V131CTransferProgramRerunCommandSheetReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
        chain_rows: list[dict[str, Any]] = []
        seen = set()
        for artifact in protocol["artifact_rows"]:
            rerun_chain = artifact["rerun_chain"]
            if rerun_chain in seen:
                continue
            seen.add(rerun_chain)
            commands = RERUN_CHAIN_COMMANDS[rerun_chain]
            chain_rows.append(
                {
                    "rerun_chain": rerun_chain,
                    "command_count": len(commands),
                    "commands": commands,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v131c_transfer_program_rerun_command_sheet_v1",
            "rerun_chain_count": len(chain_rows),
            "authoritative_status": "rerun_command_sheet_ready_but_only_to_be_used_after_change_gate_opens",
            "authoritative_rule": "do_not_execute_any_rerun_chain_while_v130z_says_rerun_required_false",
        }
        interpretation = [
            "V1.31C converts the monitored artifact protocol into explicit rerun command sheets.",
            "This removes ambiguity after a future data change: once the gate opens, the exact rerun sequence is already defined.",
        ]
        return V131CTransferProgramRerunCommandSheetReport(
            summary=summary,
            chain_rows=chain_rows,
            interpretation=interpretation,
        )

    def write_markdown(self, rows: list[dict[str, Any]]) -> Path:
        lines = ["# Transfer Program Rerun Command Sheet", ""]
        for row in rows:
            lines.append(f"## {row['rerun_chain']}")
            for command in row["commands"]:
                lines.append(f"- `{command}`")
            lines.append("")
        self.output_md_path.write_text("\n".join(lines), encoding="utf-8")
        return self.output_md_path


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131CTransferProgramRerunCommandSheetReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V131CTransferProgramRerunCommandSheetAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131c_transfer_program_rerun_command_sheet_v1",
        result=result,
    )
    analyzer.write_markdown(result.chain_rows)


if __name__ == "__main__":
    main()
