from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112WPhaseCharterReport:
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


class V112WPhaseCharterAnalyzer:
    def analyze(self, *, v112v_phase_closure_payload: dict[str, Any]) -> V112WPhaseCharterReport:
        closure_summary = dict(v112v_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112v_waiting_state_now")):
            raise ValueError("V1.12W requires V1.12V to have lawfully closed.")

        charter = {
            "phase_name": "V1.12W CPO Future Catalyst Calendar Operationalization",
            "mission": (
                "Turn the frozen future-visible CPO catalyst anchors into an operational recurring calendar table so "
                "forward event timing can later be attached consistently without mixing it with execution logic."
            ),
            "in_scope": [
                "operationalize the future catalyst calendar gap called out in V1.12U",
                "freeze a bounded recurring calendar table schema",
                "freeze cadence, bucket, and confidence fields for forward-visible catalyst rows",
            ],
            "out_of_scope": [
                "daily board chronology backfill",
                "spillover factor testing",
                "adjacent role split cleanup",
                "training authorization",
                "signal generation",
            ],
            "success_criteria": [
                "future-visible catalyst anchors are turned into an operational calendar target rather than a loose list",
                "the calendar has explicit recurring fields and review flags",
                "forward catalyst handling is auditable and separated from execution semantics",
            ],
            "stop_criteria": [
                "the phase turns into event prediction or trigger logic",
                "the phase silently opens training or signal work",
                "the calendar is widened into general macro scheduling beyond the CPO line",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112w_cpo_future_catalyst_calendar_operationalization",
            "do_open_v112w_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112w_cpo_future_catalyst_calendar_operationalization_v1",
        }
        interpretation = [
            "V1.12W attacks one remaining material gap from V1.12U.",
            "It stays in the information-foundation layer and does not authorize training or execution.",
            "The purpose is operational clarity for future-visible catalysts, not prediction.",
        ]
        return V112WPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112w_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112WPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
