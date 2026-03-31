from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V110AProbeProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V110AProbeProtocolAnalyzer:
    """Freeze the protocol for a single bounded cross-family probe."""

    def analyze(
        self,
        *,
        v110a_phase_charter_payload: dict[str, Any],
        v19_feature_breadth_rereview_payload: dict[str, Any],
    ) -> V110AProbeProtocolReport:
        charter_summary = dict(v110a_phase_charter_payload.get("summary", {}))
        rereview_rows = list(v19_feature_breadth_rereview_payload.get("review_rows", []))

        if not bool(charter_summary.get("do_open_v110a_now")):
            raise ValueError("V1.10A charter must be open before the probe protocol can be frozen.")

        target_row = next(
            (dict(row) for row in rereview_rows if str(row.get("feature_name", "")) == "policy_followthrough_support"),
            {},
        )
        protocol = {
            "target_feature_name": "policy_followthrough_support",
            "existing_symbol_family_anchor": sorted(
                set(str(symbol) for symbol in target_row.get("new_admitted_symbols", []))
            ),
            "candidate_source_pool": "closed_followthrough_like_lanes_with_policy_or_industry_context",
            "sample_limit": 2,
            "required_non_redundancy_axes": [
                "cross_symbol_family",
                "catalyst_context_not_identical",
                "not_same_event_day_same_symbol_cluster",
            ],
            "forbidden_actions": [
                "retained_feature_promotion",
                "strategy_integration",
                "new_refresh_opening",
                "automatic_v110b_creation",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v110a_probe_protocol_v1",
            "target_feature_name": protocol["target_feature_name"],
            "allow_zero_admitted_as_successful_probe": True,
            "sample_limit": protocol["sample_limit"],
            "ready_for_single_probe_next": True,
        }
        interpretation = [
            "V1.10A is a single bounded probe, not an expansion phase.",
            "A candidate must be cross-family and non-redundant relative to the current 300750-based evidence anchor.",
            "Zero admitted cases is a valid successful negative result if the bounded pool cannot satisfy the frozen gate.",
        ]
        return V110AProbeProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v110a_probe_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V110AProbeProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
