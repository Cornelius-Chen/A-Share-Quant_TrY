from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BQPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BQPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bp_phase_closure_payload: dict[str, Any],
        v112bh_phase_closure_payload: dict[str, Any],
        v112bn_phase_closure_payload: dict[str, Any],
        v112bo_phase_closure_payload: dict[str, Any],
        v112bl_phase_closure_payload: dict[str, Any],
    ) -> V112BQPhaseCharterReport:
        required = [
            ("V1.12BP", v112bp_phase_closure_payload, "v112bp_success_criteria_met"),
            ("V1.12BH", v112bh_phase_closure_payload, "v112bh_success_criteria_met"),
            ("V1.12BN", v112bn_phase_closure_payload, "v112bn_success_criteria_met"),
            ("V1.12BO", v112bo_phase_closure_payload, "v112bo_success_criteria_met"),
            ("V1.12BL", v112bl_phase_closure_payload, "v112bl_success_criteria_met"),
        ]
        for phase_name, payload, flag_name in required:
            if not bool(dict(payload.get("summary", {})).get(flag_name)):
                raise ValueError(f"{phase_name} must be closed before V1.12BQ can open.")

        charter = {
            "phase_name": "V1.12BQ CPO Gate Precision Sweep",
            "mission": (
                "Treat the fusion selector as fixed alpha backbone, then run a bounded coarse-to-fine sweep on "
                "eligibility and veto thresholds to compress drawdown toward the neutral baseline without "
                "collapsing participation into all-cash behavior."
            ),
            "in_scope": [
                "coarse-to-fine gate threshold sweep on top of the frozen fusion selector",
                "neutral-style eligibility skeleton reuse",
                "internal maturity overlay veto precision",
                "regime support as auxiliary threshold only",
                "report-only evaluation against fusion and neutral baselines",
            ],
            "out_of_scope": [
                "new selector family expansion",
                "formal training opening",
                "formal signal generation",
                "row-geometry widening",
                "promotion of unsupervised bundles into truth",
            ],
            "success_criteria": [
                "the sweep produces at least one non-cash candidate configuration",
                "best candidate is evaluated on return retention and drawdown compression together",
                "the phase outputs candidate gate or veto rules rather than abstract observations",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bq_cpo_gate_precision_sweep",
            "do_open_v112bq_now": True,
            "recommended_first_action": "freeze_v112bq_cpo_gate_precision_sweep_v1",
        }
        interpretation = [
            "V1.12BQ exists because the main bottleneck is no longer selector quality; it is eligibility discipline.",
            "Teacher decomposition and regime-only gating both failed to replace the neutral baseline on their own, so the lawful next step is a bounded threshold sweep on top of the frozen selector backbone.",
        ]
        return V112BQPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bq_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BQPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
