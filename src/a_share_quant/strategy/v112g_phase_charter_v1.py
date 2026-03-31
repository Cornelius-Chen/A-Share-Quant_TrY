from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112GPhaseCharterReport:
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


class V112GPhaseCharterAnalyzer:
    """Open the bounded catalyst-state semantics v2 rerun phase."""

    def analyze(
        self,
        *,
        v112f_phase_closure_payload: dict[str, Any],
    ) -> V112GPhaseCharterReport:
        closure_summary = dict(v112f_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112f_success_criteria_met")):
            raise ValueError("V1.12G requires V1.12F closure before opening.")

        charter = {
            "phase_name": "V1.12G Catalyst-State Semantics V2 Rerun",
            "mission": (
                "Add three bounded catalyst-state semantic features and rerun the same pilot baseline plus GBDT sidecar "
                "on the same frozen dataset to test whether hotspot optimism improves."
            ),
            "in_scope": [
                "freeze a catalyst-state feature schema v2",
                "rerun the nearest-centroid baseline on the same frozen pilot dataset",
                "rerun the GBDT sidecar on the same frozen pilot dataset",
                "compare v2 hotspot metrics against v1 baseline and v1 GBDT",
            ],
            "out_of_scope": [
                "dataset widening",
                "new symbols",
                "intraday features",
                "deployment",
                "new model families beyond the bounded GBDT rerun",
            ],
            "success_criteria": [
                "the v2 feature schema is explicit and bounded",
                "the same frozen dataset can be rerun with the new features",
                "the rerun changes hotspot metrics enough to inform the next feature/label decision",
            ],
            "stop_criteria": [
                "the v2 semantics cannot be expressed without changing data scope",
                "the rerun drifts into a new model search rather than a same-scope comparison",
                "the result adds no decision value beyond V1.12F",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112g_now_for_catalyst_state_v2_rerun",
            "do_open_v112g_now": True,
            "ready_for_feature_schema_v2_next": True,
        }
        interpretation = [
            "V1.12G keeps the same data and labels, but upgrades catalyst-state representation.",
            "The phase exists to test representation value, not to search for a new model family.",
            "The correct output is a same-scope before/after comparison on known hotspot stages.",
        ]
        return V112GPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112g_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
