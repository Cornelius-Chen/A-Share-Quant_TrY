from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129OCommercialAerospaceBK0480PortabilityBoundaryMemoReport:
    summary: dict[str, Any]
    portable_carry_rows: list[dict[str, Any]]
    local_reset_rows: list[dict[str, Any]]
    governance_carry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "portable_carry_rows": self.portable_carry_rows,
            "local_reset_rows": self.local_reset_rows,
            "governance_carry_rows": self.governance_carry_rows,
            "interpretation": self.interpretation,
        }


class V129OCommercialAerospaceBK0480PortabilityBoundaryMemoAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.selection_path = repo_root / "reports" / "analysis" / "v129n_commercial_aerospace_transfer_target_selection_v1.json"
        self.portability_path = repo_root / "reports" / "analysis" / "v128k_commercial_aerospace_portability_packaging_v1.json"
        self.governance_path = repo_root / "reports" / "analysis" / "v129k_commercial_aerospace_governance_stack_packaging_v1.json"

    def analyze(self) -> V129OCommercialAerospaceBK0480PortabilityBoundaryMemoReport:
        selection = json.loads(self.selection_path.read_text(encoding="utf-8"))
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))
        governance = json.loads(self.governance_path.read_text(encoding="utf-8"))

        portable_carry_rows = [
            {
                "layer": row["layer"],
                "rule": row["rule"],
                "transfer_action": "carry_forward_as_methodology",
                "bk0480_requirement": "relearn_board_local_thresholds_and_symbols_before_binding_to_replay",
            }
            for row in portability["portable_rows"]
        ]

        local_reset_rows = [
            {
                "layer": row["layer"],
                "commercial_aerospace_local_rule": row["rule"],
                "reset_action": "reset_to_unknown_then_relearn_on_bk0480",
                "why": row["why_local_only"],
            }
            for row in portability["local_only_rows"]
        ]

        governance_carry_rows = [
            {
                "layer": "timechain_transparency",
                "transfer_action": "carry_schema_only",
                "bk0480_requirement": "rebuild_signal_execution_preopen_triplets_from_bk0480 replay rows",
            },
            {
                "layer": "preopen_decisive_event_governance",
                "transfer_action": "carry_governance_logic_only",
                "bk0480_requirement": "rebuild decisive-event registry from BK0480-specific catalysts and adverse watches",
            },
            {
                "layer": "failure_library",
                "transfer_action": "carry_library_schema_only",
                "bk0480_requirement": "start empty and populate only with BK0480 lawful-but-suspicious cases",
            },
            {
                "layer": "phase_state_machine",
                "transfer_action": "carry_state_machine_shape_only",
                "bk0480_requirement": "relearn probe/full-pre/full/de-risk boundaries without importing commercial-aerospace windows",
            },
            {
                "layer": "phase_specific_walk_forward",
                "transfer_action": "carry_validation_method_only",
                "bk0480_requirement": "derive new lawful folds from BK0480 chronology instead of reusing commercial-aerospace split geometry",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129o_commercial_aerospace_bk0480_portability_boundary_memo_v1",
            "selected_transfer_target": selection["summary"]["recommended_primary_transfer_target"],
            "selected_transfer_board_name": selection["summary"]["recommended_primary_transfer_board_name"],
            "portable_layer_count": len(portable_carry_rows),
            "local_reset_layer_count": len(local_reset_rows),
            "governance_carry_layer_count": len(governance_carry_rows),
            "authoritative_rule": "carry_portable_grammar_and_governance_schema_but_reset_all_local_chronology_symbol_and_rule_name_semantics_before_bk0480_replay",
            "governance_stack_count": governance["summary"]["governance_layer_count"],
        }
        interpretation = [
            "V1.29O formalizes the boundary between transferable commercial-aerospace method and BK0480-local semantics.",
            "This memo is designed to prevent silent over-transfer before any BK0480 board worker opens replay logic.",
        ]
        return V129OCommercialAerospaceBK0480PortabilityBoundaryMemoReport(
            summary=summary,
            portable_carry_rows=portable_carry_rows,
            local_reset_rows=local_reset_rows,
            governance_carry_rows=governance_carry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129OCommercialAerospaceBK0480PortabilityBoundaryMemoReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_reset_sheet(
    *,
    output_path: Path,
    result: V129OCommercialAerospaceBK0480PortabilityBoundaryMemoReport,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "layer",
                "commercial_aerospace_local_rule",
                "reset_action",
                "why",
            ],
        )
        writer.writeheader()
        writer.writerows(result.local_reset_rows)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129OCommercialAerospaceBK0480PortabilityBoundaryMemoAnalyzer(repo_root).analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129o_commercial_aerospace_bk0480_portability_boundary_memo_v1",
        result=result,
    )
    write_reset_sheet(
        output_path=repo_root
        / "data"
        / "training"
        / "commercial_aerospace_to_bk0480_local_reset_sheet_v1.csv",
        result=result,
    )
    print(report_path)


if __name__ == "__main__":
    main()
