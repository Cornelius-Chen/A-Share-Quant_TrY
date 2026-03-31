from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111APhaseCharterReport:
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


class V111APhaseCharterAnalyzer:
    """Open the first bounded pilot on top of the V1.11 acquisition basis."""

    def analyze(
        self,
        *,
        v111_phase_closure_payload: dict[str, Any],
        owner_phase_switch_approved: bool,
    ) -> V111APhaseCharterReport:
        closure_summary = dict(v111_phase_closure_payload.get("summary", {}))
        ready_for_pilot = bool(closure_summary.get("ready_for_bounded_first_pilot_next"))
        do_open_now = ready_for_pilot and owner_phase_switch_approved

        charter = {
            "mission": (
                "Execute one owner-reviewed bounded first catalyst acquisition pilot under the frozen "
                "V1.11 infrastructure to test whether new non-anchor, point-in-time, source-aware, "
                "market-confirmed sustained-catalyst candidates can be admitted."
            ),
            "in_scope": [
                "bounded candidate screening under frozen source hierarchy",
                "admission against frozen admissibility and family novelty rules",
                "candidate recording for newly admitted non-anchor cases",
                "pilot-only collection summary",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "generic replay growth",
                "automatic follow-on pilot phases",
                "same-pool policy-followthrough re-probing",
            ],
            "success_criteria": [
                "screen the first bounded candidate pool under V1.11 rules",
                "admit at least one lawful non-anchor candidate or close with a clear negative result",
                "stay within candidate and admission caps",
                "record feature-shadow implications without opening promotion",
            ],
            "stop_criteria": [
                "candidate cap reached",
                "admission cap reached",
                "all screened rows fail frozen admissibility or novelty rules",
                "the branch drifts into promotion or strategy arguments",
            ],
            "handoff_condition": (
                "After the pilot collection summary, the branch must close and return to waiting state "
                "unless the owner explicitly opens another phase."
            ),
            "exploration_layer_phase": True,
            "owner_reviewed_exception_phase": True,
            "auto_follow_on_forbidden": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v111a_bounded_first_catalyst_acquisition_pilot"
                if do_open_now
                else "hold_v111a_until_owner_approves_bounded_first_pilot"
            ),
            "do_open_v111a_now": do_open_now,
            "ready_for_bounded_first_pilot_next": ready_for_pilot,
            "owner_phase_switch_approved": owner_phase_switch_approved,
            "recommended_first_action": "freeze_v111a_screened_collection_protocol_v1",
        }
        interpretation = [
            "V1.11A is not a new acquisition-design phase; it is the first bounded execution pilot on top of the frozen acquisition basis.",
            "The pilot remains exploration-layer only and cannot promote features or auto-open later phases.",
            "The next legal action is a screened collection protocol that turns V1.11 rules into a small executable pilot.",
        ]
        return V111APhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v111a_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111APhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
