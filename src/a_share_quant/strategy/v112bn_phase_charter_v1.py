from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BNPhaseCharterReport:
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


class V112BNPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bc_phase_closure_payload: dict[str, Any],
        v112bd_phase_closure_payload: dict[str, Any],
        v112be_phase_closure_payload: dict[str, Any],
        v112bf_phase_closure_payload: dict[str, Any],
        v112bg_phase_closure_payload: dict[str, Any],
        v112bh_phase_closure_payload: dict[str, Any],
        v112bi_phase_closure_payload: dict[str, Any],
        v112bj_phase_closure_payload: dict[str, Any],
        v112az_phase_closure_payload: dict[str, Any],
        v112z_phase_closure_payload: dict[str, Any],
        v112bb_phase_closure_payload: dict[str, Any],
    ) -> V112BNPhaseCharterReport:
        closure_payloads = [
            ("V1.12BC", v112bc_phase_closure_payload, "v112bc_success_criteria_met"),
            ("V1.12BD", v112bd_phase_closure_payload, "v112bd_success_criteria_met"),
            ("V1.12BE", v112be_phase_closure_payload, "v112be_success_criteria_met"),
            ("V1.12BF", v112bf_phase_closure_payload, "v112bf_success_criteria_met"),
            ("V1.12BG", v112bg_phase_closure_payload, "v112bg_success_criteria_met"),
            ("V1.12BH", v112bh_phase_closure_payload, "v112bh_success_criteria_met"),
            ("V1.12BI", v112bi_phase_closure_payload, "v112bi_success_criteria_met"),
            ("V1.12BJ", v112bj_phase_closure_payload, "v112bj_success_criteria_met"),
            ("V1.12AZ", v112az_phase_closure_payload, "v112az_success_criteria_met"),
            ("V1.12Z", v112z_phase_closure_payload, "v112z_success_criteria_met"),
            ("V1.12BB", v112bb_phase_closure_payload, "v112bb_success_criteria_met"),
        ]
        for phase_name, payload, flag_name in closure_payloads:
            if not bool(dict(payload.get("summary", {})).get(flag_name)):
                raise ValueError(f"{phase_name} must be closed before V1.12BN can open.")

        charter = {
            "phase_name": "V1.12BN CPO Teacher Decomposition Gate Search",
            "mission": (
                "Approximate the current neutral selective CPO teacher by brute-force decomposing its gate into "
                "multiple quantized conditions and small regime overlays, while staying no-leak and report-only."
            ),
            "in_scope": [
                "bounded condition-subset search on the lawful 10-row CPO layer",
                "quantized thresholds for probability margin, confidence tier, rollforward, turnover cap, breadth floor, and catalyst floor",
                "optional regime overlay thresholds when locally available",
                "teacher alignment metrics plus portfolio metrics",
                "comparison against neutral, aggressive, ranker, and oracle tracks",
            ],
            "out_of_scope": [
                "heavy deep models",
                "reinforcement learning",
                "deployment",
                "formal signal generation",
                "unbounded model-zoo expansion",
            ],
            "success_criteria": [
                "the search remains no-leak and report-only",
                "it enumerates bounded candidate decompositions with explicit metrics",
                "it proves whether a non-cash candidate can materially approximate the neutral teacher or documents why none can",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bn_teacher_decomposition_gate_search",
            "do_open_v112bn_now": True,
            "recommended_first_action": "freeze_v112bn_teacher_decomposition_gate_search_v1",
        }
        interpretation = [
            "V1.12BN is a bounded factorization search, not a new portfolio ideology.",
            "It tests whether the neutral selective teacher can be approximated by cheap rule decomposition rather than a monolithic learned gate.",
        ]
        return V112BNPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bn_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BNPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
