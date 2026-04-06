from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V126RCommercialAerospacePQRExecutionPruningTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V126RCommercialAerospacePQRExecutionPruningTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.reference_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.audit_path = repo_root / "reports" / "analysis" / "v126p_commercial_aerospace_execution_surface_pruning_audit_v1.json"
        self.replay_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"

    def analyze(self) -> V126RCommercialAerospacePQRExecutionPruningTriageReport:
        reference = json.loads(self.reference_path.read_text(encoding="utf-8"))["summary"]
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        replay = json.loads(self.replay_path.read_text(encoding="utf-8"))["summary"]
        best_name = audit["summary"]["best_variant"]
        best_row = next(row for row in audit["variant_rows"] if row["variant"] == best_name)

        improves_equity = replay["final_equity"] >= reference["final_equity"]
        improves_dd = replay["max_drawdown"] <= reference["max_drawdown"]
        materially_cuts_orders = replay["executed_order_count"] <= reference["executed_order_count"] * 0.65
        authoritative_status = (
            "retained_shadow_execution_surface_pruned"
            if improves_equity and improves_dd and materially_cuts_orders
            else "keep_v126o_reference_and_block_pruning_promotion"
        )

        summary = {
            "acceptance_posture": "freeze_v126r_commercial_aerospace_pqr_execution_pruning_triage_v1",
            "reference_final_equity": reference["final_equity"],
            "reference_max_drawdown": reference["max_drawdown"],
            "reference_executed_order_count": reference["executed_order_count"],
            "best_pruning_variant": best_name,
            "best_pruning_variant_final_equity": best_row["final_equity"],
            "best_pruning_variant_max_drawdown": best_row["max_drawdown"],
            "best_pruning_variant_executed_order_count": best_row["executed_order_count"],
            "selected_replay_final_equity": replay["final_equity"],
            "selected_replay_max_drawdown": replay["max_drawdown"],
            "selected_replay_executed_order_count": replay["executed_order_count"],
            "authoritative_status": authoritative_status,
        }
        interpretation = [
            "V1.26R only promotes execution-surface pruning if it preserves or improves economics while materially reducing churn.",
            "If pruning mainly beautifies the replay but gives back too much economics, V1.26O remains the reference shadow.",
        ]
        return V126RCommercialAerospacePQRExecutionPruningTriageReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126RCommercialAerospacePQRExecutionPruningTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126RCommercialAerospacePQRExecutionPruningTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126r_commercial_aerospace_pqr_execution_pruning_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
