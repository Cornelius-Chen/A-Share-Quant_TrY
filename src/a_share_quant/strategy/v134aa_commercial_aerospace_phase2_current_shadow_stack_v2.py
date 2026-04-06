from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AACommercialAerospacePhase2CurrentShadowStackV2Report:
    summary: dict[str, Any]
    stack_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stack_rows": self.stack_rows,
            "interpretation": self.interpretation,
        }


class V134AACommercialAerospacePhase2CurrentShadowStackV2Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.seed_attr_path = analysis_dir / "v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1.json"
        self.base_wide_path = analysis_dir / "v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.json"
        self.mild_block_path = analysis_dir / "v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.json"
        self.late_severe_block_path = analysis_dir / "v134x_commercial_aerospace_reversal_late_severe_block_audit_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_current_shadow_stack_v2.csv"
        )

    def analyze(self) -> V134AACommercialAerospacePhase2CurrentShadowStackV2Report:
        seed_attr = json.loads(self.seed_attr_path.read_text(encoding="utf-8"))
        base_wide = json.loads(self.base_wide_path.read_text(encoding="utf-8"))
        mild_block = json.loads(self.mild_block_path.read_text(encoding="utf-8"))
        late_severe_block = json.loads(self.late_severe_block_path.read_text(encoding="utf-8"))

        stack_rows = [
            {
                "variant": "canonical_seed_simulator",
                "scope": "6 canonical sessions",
                "same_day_loss_avoided_total": seed_attr["summary"]["same_day_loss_avoided_total"],
                "simulated_order_count": seed_attr["summary"]["order_count"],
                "status": "retained_narrow_reference",
            },
            {
                "variant": "broader_hit_base",
                "scope": "24 broader-hit sessions",
                "same_day_loss_avoided_total": base_wide["summary"]["same_day_loss_avoided_total"],
                "simulated_order_count": base_wide["summary"]["simulated_order_count"],
                "status": "superseded",
            },
            {
                "variant": "broader_hit_mild_blocked",
                "scope": "24 broader-hit sessions",
                "same_day_loss_avoided_total": mild_block["summary"]["mild_block_same_day_loss_avoided_total"],
                "simulated_order_count": mild_block["summary"]["mild_block_simulated_order_count"],
                "status": "superseded_by_local_cluster_refinement",
            },
            {
                "variant": "broader_hit_mild_blocked_plus_reversal_late_severe_block",
                "scope": "24 broader-hit sessions",
                "same_day_loss_avoided_total": late_severe_block["summary"]["adjusted_same_day_loss_avoided_total"],
                "simulated_order_count": mild_block["summary"]["mild_block_simulated_order_count"] - 1,
                "status": "current_phase2_wider_reference",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(stack_rows[0].keys()))
            writer.writeheader()
            writer.writerows(stack_rows)

        summary = {
            "acceptance_posture": "freeze_v134aa_commercial_aerospace_phase2_current_shadow_stack_v2",
            "current_phase2_wider_reference": "broader_hit_mild_blocked_plus_reversal_late_severe_block",
            "current_phase2_narrow_reference": "canonical_seed_simulator",
            "phase2_best_same_day_loss_avoided_total": late_severe_block["summary"][
                "adjusted_same_day_loss_avoided_total"
            ],
            "phase2_best_simulated_order_count": mild_block["summary"]["mild_block_simulated_order_count"] - 1,
            "stack_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_phase2_current_shadow_stack_v2_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AA freezes the updated phase-2 shadow stack after promoting the local reversal-late-severe block.",
            "The branch now has a refined wider reference that incorporates both the predicted-mild execution block and the single-cluster late-severe correction.",
        ]
        return V134AACommercialAerospacePhase2CurrentShadowStackV2Report(
            summary=summary,
            stack_rows=stack_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AACommercialAerospacePhase2CurrentShadowStackV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AACommercialAerospacePhase2CurrentShadowStackV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134aa_commercial_aerospace_phase2_current_shadow_stack_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
