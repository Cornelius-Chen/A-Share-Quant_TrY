from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPPhaseCharterReport:
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


class V112BPPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bk_phase_closure_payload: dict[str, Any],
        v112bd_phase_closure_payload: dict[str, Any],
        v112bh_phase_closure_payload: dict[str, Any],
        v112bo_phase_closure_payload: dict[str, Any],
        v112bb_phase_closure_payload: dict[str, Any],
    ) -> V112BPPhaseCharterReport:
        required = [
            ("V1.12BK", v112bk_phase_closure_payload, "v112bk_success_criteria_met"),
            ("V1.12BD", v112bd_phase_closure_payload, "v112bd_success_criteria_met"),
            ("V1.12BH", v112bh_phase_closure_payload, "v112bh_success_criteria_met"),
            ("V1.12BO", v112bo_phase_closure_payload, "v112bo_success_criteria_met"),
            ("V1.12BB", v112bb_phase_closure_payload, "v112bb_success_criteria_met"),
        ]
        for phase_name, payload, flag_name in required:
            if not bool(dict(payload.get("summary", {})).get(flag_name)):
                raise ValueError(f"{phase_name} must be closed before V1.12BP can open.")

        charter = {
            "phase_name": "V1.12BP CPO Selector Maturity Fusion Pilot",
            "mission": (
                "Fuse the strongest lawful selector candidate with the frozen internal-maturity overlay and "
                "auxiliary market-regime overlay, then test whether drawdown can be compressed without giving up "
                "all of the selector's upside on the frozen 10-row CPO layer."
            ),
            "in_scope": [
                "best-selector reuse on the lawful 10-row training-facing layer",
                "internal maturity overlay gating",
                "market regime overlay as auxiliary context only",
                "report-only no-leak portfolio simulation",
                "comparison against BK selector, BH neutral, and BF aggressive tracks",
            ],
            "out_of_scope": [
                "formal training opening",
                "formal signal generation",
                "row-geometry widening",
                "promotion of overlays into truth labels",
            ],
            "success_criteria": [
                "the fusion line remains no-leak and report-only",
                "the internal maturity overlay is actually consumed downstream",
                "the tradeoff against neutral and BK is made explicit",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bp_cpo_selector_maturity_fusion_pilot",
            "do_open_v112bp_now": True,
            "recommended_first_action": "freeze_v112bp_cpo_selector_maturity_fusion_pilot_v1",
        }
        interpretation = [
            "V1.12BP exists because selector strength is no longer the main bottleneck; timing and maturity discipline are.",
            "The lawful next step is a selector-plus-overlay fusion, not another uncontrolled selector-only expansion.",
        ]
        return V112BPPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bp_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
