from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AQCommercialAerospacePhase2CurrentShadowStackV4Report:
    summary: dict[str, Any]
    stack_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stack_rows": self.stack_rows,
            "interpretation": self.interpretation,
        }


class V134AQCommercialAerospacePhase2CurrentShadowStackV4Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.stack_v3_path = analysis_dir / "v134ae_commercial_aerospace_phase2_current_shadow_stack_v3.json"
        self.local_deferral_path = analysis_dir / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_current_shadow_stack_v4.csv"
        )

    def analyze(self) -> V134AQCommercialAerospacePhase2CurrentShadowStackV4Report:
        stack_v3 = json.loads(self.stack_v3_path.read_text(encoding="utf-8"))
        local_deferral = json.loads(self.local_deferral_path.read_text(encoding="utf-8"))
        prior_total = float(stack_v3["summary"]["phase2_best_same_day_loss_avoided_total"])
        prior_orders = int(stack_v3["summary"]["phase2_best_simulated_order_count"])
        delta = float(local_deferral["summary"]["best_same_day_loss_avoided_delta_total"])

        stack_rows = [
            {
                "variant": "canonical_seed_simulator",
                "scope": "6 canonical sessions",
                "same_day_loss_avoided_total": 3732.6954,
                "simulated_order_count": 8,
                "status": "retained_narrow_reference",
            },
            {
                "variant": stack_v3["summary"]["current_phase2_wider_reference"],
                "scope": "24 broader-hit sessions",
                "same_day_loss_avoided_total": prior_total,
                "simulated_order_count": prior_orders,
                "status": "superseded_by_local_deferral_refinement",
            },
            {
                "variant": "broader_hit_current_plus_reversal_100pct_plus_local_reversal_deferral",
                "scope": "24 broader-hit sessions",
                "same_day_loss_avoided_total": round(prior_total + delta, 4),
                "simulated_order_count": prior_orders,
                "status": "current_phase2_wider_reference",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(stack_rows[0].keys()))
            writer.writeheader()
            writer.writerows(stack_rows)

        summary = {
            "acceptance_posture": "freeze_v134aq_commercial_aerospace_phase2_current_shadow_stack_v4",
            "current_phase2_wider_reference": "broader_hit_current_plus_reversal_100pct_plus_local_reversal_deferral",
            "current_phase2_narrow_reference": "canonical_seed_simulator",
            "phase2_best_same_day_loss_avoided_total": round(prior_total + delta, 4),
            "phase2_best_simulated_order_count": prior_orders,
            "local_deferral_same_day_delta": delta,
            "stack_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_phase2_current_shadow_stack_v4_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AQ freezes the next phase-2 stack after promoting the local reversal-deferral refinement.",
            "The wider reference stays on the same broader-hit surface, but keeps a narrower point-in-time path refinement for a tiny rebound-cost subset.",
        ]
        return V134AQCommercialAerospacePhase2CurrentShadowStackV4Report(
            summary=summary,
            stack_rows=stack_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AQCommercialAerospacePhase2CurrentShadowStackV4Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AQCommercialAerospacePhase2CurrentShadowStackV4Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134aq_commercial_aerospace_phase2_current_shadow_stack_v4",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
