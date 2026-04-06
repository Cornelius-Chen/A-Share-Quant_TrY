from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126f_commercial_aerospace_zero_trigger_audit_v1 import (
    V126FCommercialAerospaceZeroTriggerAuditAnalyzer,
)
from a_share_quant.strategy.v126g_commercial_aerospace_regime_local_shadow_replay_v1 import (
    V126GCommercialAerospaceRegimeLocalShadowReplayAnalyzer,
)
from a_share_quant.strategy.v126h_commercial_aerospace_two_layer_eligibility_audit_v1 import (
    V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer,
)
from a_share_quant.strategy.v126i_commercial_aerospace_two_layer_shadow_replay_v1 import (
    V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer,
)


@dataclass(slots=True)
class V126JCommercialAerospaceFGHTwoLayerTriageReport:
    summary: dict[str, Any]
    retained_variants: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_variants": self.retained_variants,
            "interpretation": self.interpretation,
        }


class V126JCommercialAerospaceFGHTwoLayerTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V126JCommercialAerospaceFGHTwoLayerTriageReport:
        zero_audit = V126FCommercialAerospaceZeroTriggerAuditAnalyzer(self.repo_root).analyze()
        baseline = V126GCommercialAerospaceRegimeLocalShadowReplayAnalyzer(self.repo_root).analyze()
        layer_audit = V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer(self.repo_root).analyze()
        two_layer = V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer(self.repo_root).analyze()

        improved = [
            row for row in two_layer.variant_rows
            if row["final_equity"] > baseline.summary["final_equity"] and row["max_drawdown"] <= baseline.summary["max_drawdown"]
        ]
        best_variant = max(two_layer.variant_rows, key=lambda row: row["final_equity"])
        summary = {
            "acceptance_posture": "freeze_v126j_commercial_aerospace_fgh_two_layer_triage_v1",
            "baseline_final_equity": baseline.summary["final_equity"],
            "baseline_max_drawdown": baseline.summary["max_drawdown"],
            "zero_trigger_root_cause_confirmed": zero_audit.summary["global_threshold_impulse_hits"] == 0 and zero_audit.summary["regime_local_threshold_impulse_hits"] > 0,
            "impulse_train_full_count": layer_audit.summary["impulse_train_full_count"],
            "two_layer_improving_variant_count": len(improved),
            "best_variant_name": best_variant["variant_name"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
            "authoritative_status": "two_layer_shadow_variant_retained_for_next_review" if improved else "two_layer_shadow_design_blocked_keep_regime_local_reference_only",
        }
        interpretation = [
            "V1.26J freezes whether probe/full score stratification deserves to survive after the first lawful replay became non-zero.",
            "A two-layer design only survives if it beats the V1.26G regime-local reference without worsening drawdown.",
        ]
        return V126JCommercialAerospaceFGHTwoLayerTriageReport(summary=summary, retained_variants=improved if improved else [best_variant], interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126JCommercialAerospaceFGHTwoLayerTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126JCommercialAerospaceFGHTwoLayerTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126j_commercial_aerospace_fgh_two_layer_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
