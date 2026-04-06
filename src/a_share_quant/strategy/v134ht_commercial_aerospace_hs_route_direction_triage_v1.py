from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hs_commercial_aerospace_training_target_route_audit_v1 import (
    V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HTCommercialAerospaceHSRouteDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HTCommercialAerospaceHSRouteDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HTCommercialAerospaceHSRouteDirectionTriageV1Report:
        audit = V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "target_area": "negative_environment_semantics",
                "direction": "promote_as_next_main_supervision_target",
            },
            {
                "target_area": "event_attention_layer",
                "direction": "promote_immediately_after_negative_environment_semantics",
            },
            {
                "target_area": "capital_selection_layer",
                "direction": "defer_until_attention_anchor_and_decoy_labels_exist",
            },
            {
                "target_area": "state_machine_integration",
                "direction": "keep_as_future_supervision_integration_not_execution_binding",
            },
            {
                "target_area": "future_shadow_modules",
                "direction": "keep_blocked_until_explicit_future_shift_and_richer_label_stack",
            },
            {
                "target_area": "manifold_learning",
                "direction": "treat_as_optional_late_representation_experiment_not_current_mainline",
            },
            {
                "target_area": "execution_authority",
                "direction": "keep_blocked_do_not_pretend_current_route_is_execution_ready",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ht_commercial_aerospace_hs_route_direction_triage_v1",
            "roadmap_phase_count": audit.summary["roadmap_phase_count"],
            "agent_consensus_count": audit.summary["agent_consensus_count"],
            "authoritative_status": "retain_staged_training_route_with_environment_and_event_attention_supervision_first_execution_still_blocked",
        }
        interpretation = [
            "V1.34HT converts the roadmap audit into direction.",
            "The route is explicitly staged: learn environment distortion and event-attention divergence first, only then learn capital selection and later state-machine integration.",
        ]
        return V134HTCommercialAerospaceHSRouteDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HTCommercialAerospaceHSRouteDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HTCommercialAerospaceHSRouteDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ht_commercial_aerospace_hs_route_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
