from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18BPhaseCharterReport:
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


class V18BPhaseCharterAnalyzer:
    """Open V1.8B after V1.8A closes with explicit breadth-entry design."""

    def analyze(
        self,
        *,
        v18a_phase_closure_payload: dict[str, Any],
        v18a_breadth_entry_design_payload: dict[str, Any],
    ) -> V18BPhaseCharterReport:
        closure_summary = dict(v18a_phase_closure_payload.get("summary", {}))
        design_summary = dict(v18a_breadth_entry_design_payload.get("summary", {}))
        entry_rows = list(v18a_breadth_entry_design_payload.get("entry_rows", []))

        v18a_waiting_ready = bool(closure_summary.get("enter_v18a_waiting_state_now"))
        open_v18b_now = v18a_waiting_ready and design_summary.get("entry_row_count", 0) > 0
        target_features = [str(row.get("feature_name", "")) for row in entry_rows]

        charter = {
            "mission": "Freeze the bounded admission rules that decide which candidate breadth samples may enter future bounded collection for the current sample-breadth target features, without collecting samples now.",
            "in_scope": [
                "breadth sample admission protocol",
                "per-feature admission gate rules",
                "priority ordering rules under sample limits",
                "bounded exclusion rules for noisy or misaligned candidates",
            ],
            "out_of_scope": [
                "sample collection",
                "retained-feature promotion",
                "strategy integration",
                "cross-pocket or cross-regime validation work",
                "safe-consumption validation work",
                "generic replay growth",
            ],
            "success_criteria": [
                "freeze a bounded breadth sample admission protocol",
                "produce per-feature admission gate judgments",
                "define admission priority rules under current sample limits",
                "close the phase with a clear admission-gate readiness posture or bounded hold posture",
            ],
            "stop_criteria": [
                "if admission gating drifts into actual sample collection",
                "if admission rules cannot stay tied to the frozen breadth-entry design",
                "if no bounded exclusion logic can be written without weakening current evidence standards",
            ],
            "handoff_condition": "After the charter opens, only replay-independent admission-gate artifacts are allowed until a bounded collection-entry posture is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v18b_breadth_sample_admission_gate"
                if open_v18b_now
                else "hold_v18b_charter_until_prerequisites_hold"
            ),
            "v18a_waiting_state_present": v18a_waiting_ready,
            "breadth_entry_row_count": design_summary.get("entry_row_count", 0),
            "target_feature_names": target_features,
            "do_open_v18b_now": open_v18b_now,
            "recommended_first_action": "freeze_v18b_sample_admission_protocol_v1",
        }
        interpretation = [
            "V1.8A already answered where breadth evidence could legally come from, but not which candidates inside those pools are admissible.",
            "The next lawful question is therefore admission gating, not immediate sample collection.",
            "So V1.8B should open as a bounded breadth sample admission phase, not as a collection or promotion phase.",
        ]
        return V18BPhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v18b_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18BPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
