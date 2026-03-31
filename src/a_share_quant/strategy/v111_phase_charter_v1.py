from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111PhaseCharterReport:
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


class V111PhaseCharterAnalyzer:
    """Open V1.11 as sustained catalyst evidence acquisition infrastructure."""

    def analyze(
        self,
        *,
        solution_shift_memo_payload: dict[str, Any],
    ) -> V111PhaseCharterReport:
        memo_summary = dict(solution_shift_memo_payload.get("summary", {}))
        memo = dict(solution_shift_memo_payload.get("memo", {}))

        do_open_now = bool(memo_summary.get("do_open_v111_now")) and memo.get("memo_type") == "Data Acquisition Plan"

        charter = {
            "mission": "Build sustained catalyst evidence acquisition infrastructure that can repeatedly produce new point-in-time, source-aware, market-confirmed followthrough and carry-capable evidence candidates.",
            "in_scope": [
                "acquisition scope definition",
                "source hierarchy",
                "admissibility rules",
                "family novelty rules",
                "point-in-time recording rules",
                "refresh cadence",
                "bounded first-pilot plan",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "same-pool policy-followthrough re-probing",
                "wide replay expansion",
                "heavy dependency introduction",
            ],
            "success_criteria": [
                "define what sustained catalyst evidence should be collected",
                "freeze source hierarchy and admissibility rules",
                "freeze family novelty and point-in-time recording rules",
                "state a bounded first-pilot collection plan",
            ],
            "stop_criteria": [
                "if the phase drifts into ad hoc case scavenging",
                "if the phase proposes direct strategy integration",
                "if the phase cannot produce a reusable acquisition protocol",
            ],
            "handoff_condition": "After opening, only exploration-layer infrastructure design artifacts are allowed until the acquisition basis is explicit.",
            "exploration_layer_phase": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v111_sustained_catalyst_evidence_acquisition_infrastructure"
                if do_open_now
                else "hold_v111_until_solution_shift_memo_selects_data_acquisition"
            ),
            "solution_shift_memo_type": memo.get("memo_type"),
            "primary_bottleneck_category": memo.get("current_primary_bottleneck_category"),
            "do_open_v111_now": do_open_now,
            "recommended_first_action": "freeze_v111_acquisition_infrastructure_plan_v1",
        }
        interpretation = [
            "V1.11 is not a case-hunt phase; it is an exploration-layer infrastructure phase.",
            "Its purpose is to create a repeatable upstream evidence source rather than to patch the old pool with one-off finds.",
            "The next legal action is an acquisition infrastructure plan, not replay or promotion.",
        ]
        return V111PhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v111_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
