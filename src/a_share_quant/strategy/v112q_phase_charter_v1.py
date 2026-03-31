from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112QPhaseCharterReport:
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


class V112QPhaseCharterAnalyzer:
    """Freeze the full schema before more CPO collection expands."""

    def analyze(
        self,
        *,
        v112p_phase_closure_payload: dict[str, Any],
        owner_requires_schema_hardening: bool,
        owner_requires_pre_rise_window: bool,
        owner_allows_parallel_collection_drafts: bool,
    ) -> V112QPhaseCharterReport:
        closure_summary = dict(v112p_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112p_waiting_state_now")):
            raise ValueError("V1.12Q requires V1.12P to have closed into waiting state.")

        do_open_now = (
            owner_requires_schema_hardening
            and owner_requires_pre_rise_window
            and owner_allows_parallel_collection_drafts
        )
        charter = {
            "phase_name": "V1.12Q CPO Information Registry Schema V1",
            "mission": (
                "Freeze a harder CPO full-cycle registry schema with pre-rise coverage, layered feature slots, "
                "cohort buckets, and subagent-safe collection routes so later collection lowers omission risk "
                "without losing governance."
            ),
            "in_scope": [
                "freeze a full CPO registry schema above the earlier broad registry",
                "add explicit pre-ignition watch coverage before the rise window",
                "separate stock buckets from board and event-route buckets",
                "assign review-first feature slots for each information layer",
                "freeze bounded repetitive collection work that subagents may execute safely",
            ],
            "out_of_scope": [
                "automatic truth validation of all cohort rows",
                "automatic dataset widening into training",
                "formal model feature promotion",
                "execution timing logic",
                "signal generation",
            ],
            "success_criteria": [
                "the CPO line has a schema that makes omissions more traceable rather than only a flat registry",
                "pre-rise information collection becomes explicit instead of implied",
                "repetitive collection tasks are constrained tightly enough to parallelize without governance drift",
            ],
            "stop_criteria": [
                "the phase turns review-only slots into automatic training features",
                "the phase collapses different cohort buckets into one object pool",
                "the phase uses subagents for schema legislation instead of repetitive collection drafts",
            ],
            "handoff_condition": (
                "After schema freeze, the next lawful move is bounded collection drafting against the frozen schema, "
                "not automatic training or feature candidacy."
            ),
        }
        summary = {
            "acceptance_posture": (
                "open_v112q_cpo_information_registry_schema_v1"
                if do_open_now
                else "hold_v112q_until_owner_requires_schema_hardening"
            ),
            "do_open_v112q_now": do_open_now,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112q_cpo_information_registry_schema_v1",
            "owner_requires_pre_rise_window": owner_requires_pre_rise_window,
            "owner_allows_parallel_collection_drafts": owner_allows_parallel_collection_drafts,
        }
        interpretation = [
            "V1.12Q does not replace the broad V1.12P registry; it hardens it into a schema suitable for lower-omission follow-up.",
            "Pre-rise information capture is explicit because many useful CPO signals begin before the visible markup phase.",
            "Subagents are allowed only at the repetitive collection layer, not at the schema-legislation layer.",
        ]
        return V112QPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112q_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112QPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
