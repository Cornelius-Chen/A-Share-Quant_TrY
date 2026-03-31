from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113GPhaseCharterReport:
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


class V113GPhaseCharterAnalyzer:
    """Open a deep bounded archetype study for commercial-space mainline."""

    def analyze(
        self,
        *,
        v113f_phase_closure_payload: dict[str, Any],
        owner_continues_deep_study: bool,
    ) -> V113GPhaseCharterReport:
        closure_summary = dict(v113f_phase_closure_payload.get("summary", {}))
        do_open_now = bool(closure_summary.get("enter_v113f_waiting_state_now")) and owner_continues_deep_study

        charter = {
            "mission": (
                "Freeze a bounded deep-study scope for commercial_space_mainline so the project can study multi-wave "
                "theme diffusion, hierarchy, catch-up, decay, revival, and risk-monitoring behavior without leaking "
                "into execution or automatic training."
            ),
            "in_scope": [
                "owner hypothesis registry for commercial_space_mainline",
                "bounded study dimensions for multi-wave theme behavior",
                "candidate cohort tiers with explicit validation status",
                "explicit reasons why this archetype is now treated as a high-value deep study",
            ],
            "out_of_scope": [
                "label freeze",
                "model fitting",
                "execution timing",
                "signal generation",
                "automatic multi-theme expansion",
            ],
            "success_criteria": [
                "record the owner-supplied commercial-space observations as a reusable study registry",
                "separate validated local seeds from broader owner-named study candidates",
                "freeze the top study dimensions that justify deeper future work",
            ],
            "stop_criteria": [
                "if the scope drifts into execution playbooks",
                "if the phase pretends owner-named candidates are already validated",
                "if the branch expands beyond commercial_space_mainline",
            ],
            "handoff_condition": (
                "After scope freeze, the next legal move is bounded candidate validation or bounded review-sheet widening, "
                "not automatic training."
            ),
            "owner_heavy_context_phase": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v113g_commercial_space_deep_archetype_study"
                if do_open_now
                else "hold_v113g_until_owner_continuation_after_v113f_waiting_state"
            ),
            "do_open_v113g_now": do_open_now,
            "selected_archetype": "commercial_space_mainline",
            "recommended_first_action": "freeze_v113g_commercial_space_study_scope_v1",
        }
        interpretation = [
            "V1.13G does not widen the training branch yet; it widens the archetype understanding branch first.",
            "The owner input already exceeds simple object correction and now justifies a dedicated deep-study scope.",
            "The next legal move inside this phase is to freeze the study registry and candidate cohort tiers.",
        ]
        return V113GPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v113g_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113GPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
