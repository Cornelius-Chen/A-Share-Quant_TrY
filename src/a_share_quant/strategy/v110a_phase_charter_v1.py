from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V110APhaseCharterReport:
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


class V110APhaseCharterAnalyzer:
    """Open a single owner-led cross-family probe for policy followthrough breadth."""

    def analyze(
        self,
        *,
        v19_phase_closure_payload: dict[str, Any],
        v19_feature_breadth_rereview_payload: dict[str, Any],
    ) -> V110APhaseCharterReport:
        closure_summary = dict(v19_phase_closure_payload.get("summary", {}))
        rereview_rows = list(v19_feature_breadth_rereview_payload.get("review_rows", []))

        v19_waiting_ready = bool(closure_summary.get("enter_v19_waiting_state_now"))
        target_row = next(
            (dict(row) for row in rereview_rows if str(row.get("feature_name", "")) == "policy_followthrough_support"),
            {},
        )
        target_still_breadth_limited = str(target_row.get("updated_primary_shortfall", "")) == "sample_breadth_gap"
        do_open_now = v19_waiting_ready and target_still_breadth_limited

        charter = {
            "mission": "Answer one bounded question: can policy_followthrough_support obtain lawful, non-redundant, cross-symbol-family breadth evidence inside the current governed system.",
            "in_scope": [
                "policy_followthrough_support only",
                "cross-symbol-family bounded candidate screening",
                "non-redundancy check against the current 300750 symbol-family evidence",
                "report-only probe result or negative conclusion",
            ],
            "out_of_scope": [
                "single_pulse_support",
                "retained-feature promotion",
                "strategy integration",
                "new refresh opening",
                "wide replay or generic collection growth",
                "automatic follow-on micro phases",
            ],
            "success_criteria": [
                "find 1-2 lawful cross-family and non-redundant cases",
                "or conclude cleanly that no such admissible case exists in the current bounded pool",
                "close the phase without opening promotion or a successor phase automatically",
            ],
            "stop_criteria": [
                "candidate pool exhausted",
                "probe reaches the bounded sample cap",
                "admitted cases remain redundant under the frozen non-redundancy rules",
                "phase judgment becomes explicit either positive or negative",
            ],
            "handoff_condition": "After opening, only a single screened cross-family probe and its bounded phase checks are allowed.",
            "owner_led_exception_phase": True,
            "allow_auto_follow_on_phase": False,
        }
        summary = {
            "acceptance_posture": (
                "open_v110a_policy_followthrough_cross_family_breadth_probe"
                if do_open_now
                else "hold_v110a_until_breadth_limited_target_exists"
            ),
            "v19_waiting_state_present": v19_waiting_ready,
            "target_feature_name": "policy_followthrough_support",
            "target_still_breadth_limited": target_still_breadth_limited,
            "do_open_v110a_now": do_open_now,
            "recommended_first_action": "freeze_v110a_probe_protocol_v1",
        }
        interpretation = [
            "V1.9 already showed that policy_followthrough_support remains breadth-limited.",
            "That makes a single owner-led cross-family probe lawful and higher leverage than another general review.",
            "This phase is intentionally narrow and may close successfully with zero admitted cases if the current bounded pool cannot satisfy non-redundancy.",
        ]
        return V110APhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v110a_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V110APhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
