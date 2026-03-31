from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ZPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        protocol_payload: dict[str, Any],
    ) -> V112ZPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        protocol_summary = dict(protocol_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112z_as_bounded_cycle_reconstruction_only",
            "do_open_v112z_now": charter_summary.get("do_open_v112z_now"),
            "foundation_ready_for_bounded_cycle_reconstruction": protocol_summary.get(
                "foundation_ready_for_bounded_cycle_reconstruction"
            ),
            "split_ready_adjacent_asset_count": protocol_summary.get("split_ready_adjacent_asset_count"),
            "bounded_spillover_factor_candidate_count": protocol_summary.get("bounded_spillover_factor_candidate_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "run_v112z_bounded_cycle_reconstruction_pass",
        }
        evidence_rows = [
            {
                "evidence_name": "v112z_protocol",
                "actual": {
                    "foundation_ready_for_bounded_cycle_reconstruction": protocol_summary.get(
                        "foundation_ready_for_bounded_cycle_reconstruction"
                    ),
                    "split_ready_adjacent_asset_count": protocol_summary.get("split_ready_adjacent_asset_count"),
                    "bounded_spillover_factor_candidate_count": protocol_summary.get("bounded_spillover_factor_candidate_count"),
                },
                "reading": "The CPO line now has an explicit bounded reconstruction protocol and enough cleaned inputs to attempt the experiment.",
            }
        ]
        interpretation = [
            "V1.12Z remains an experiment-prep phase until the reconstruction pass itself runs.",
            "Training and feature promotion stay closed.",
        ]
        return V112ZPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112z_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
