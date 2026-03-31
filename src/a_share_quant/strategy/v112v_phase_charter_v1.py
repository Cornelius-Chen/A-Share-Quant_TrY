from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112VPhaseCharterReport:
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


class V112VPhaseCharterAnalyzer:
    def analyze(self, *, v112u_phase_closure_payload: dict[str, Any]) -> V112VPhaseCharterReport:
        closure_summary = dict(v112u_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112u_waiting_state_now")):
            raise ValueError("V1.12V requires V1.12U to have lawfully closed.")

        charter = {
            "phase_name": "V1.12V CPO Daily Board Chronology Series Operationalization",
            "mission": (
                "Turn the already-frozen CPO chronology grammar into an operational day-level board chronology table spec "
                "so board strength, breadth, turnover, and event overlap can later be attached consistently."
            ),
            "in_scope": [
                "operationalize the daily board chronology series gap called out in V1.12U",
                "freeze a bounded table schema for board chronology rows",
                "freeze source precedence and missingness handling",
            ],
            "out_of_scope": [
                "future catalyst calendar operationalization",
                "spillover factor testing",
                "adjacent role split cleanup",
                "training authorization",
                "signal generation",
            ],
            "success_criteria": [
                "the board-level chronology gap is no longer described only abstractly",
                "the project has an explicit daily chronology table spec with bounded fields",
                "source precedence and missingness are explicit enough for later collection work",
            ],
            "stop_criteria": [
                "the phase turns into bulk daily-data backfill",
                "training or feature promotion is opened implicitly",
                "the board chronology layer is widened into general market-state modeling",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112v_cpo_daily_board_chronology_operationalization",
            "do_open_v112v_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112v_cpo_daily_board_chronology_operationalization_v1",
        }
        interpretation = [
            "V1.12V attacks one explicit material gap from V1.12U.",
            "It stays in the information-foundation layer and does not authorize training.",
            "The purpose is operational clarity, not bulk data expansion.",
        ]
        return V112VPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112v_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112VPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
