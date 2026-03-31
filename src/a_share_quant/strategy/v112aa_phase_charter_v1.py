from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AAPhaseCharterReport:
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


class V112AAPhaseCharterAnalyzer:
    def analyze(self, *, v112z_reconstruction_payload: dict[str, Any]) -> V112AAPhaseCharterReport:
        reconstruction_summary = dict(v112z_reconstruction_payload.get("summary", {}))
        if not bool(reconstruction_summary.get("cycle_absorption_review_success")):
            raise ValueError("V1.12AA requires the V1.12Z reconstruction pass to have completed successfully.")

        charter = {
            "phase_name": "V1.12AA CPO Bounded Cohort Map",
            "mission": (
                "Compress the reconstructed CPO cycle into an explicit object-role-time cohort map so later "
                "labeling and black-box residual work can inherit cleaner boundaries without deleting spillover "
                "or pending ambiguity."
            ),
            "in_scope": [
                "map core, adjacent, branch-extension, spillover, and pending rows into explicit role layers",
                "attach each object to bounded stage windows rather than a timeless flat role",
                "freeze downstream admissibility notes without opening training",
            ],
            "out_of_scope": [
                "formal labeling freeze",
                "formal training rights",
                "signal generation",
                "execution implications beyond review-only decision notes",
            ],
            "success_criteria": [
                "the CPO cohort becomes readable as an object-role-time matrix",
                "spillover and pending rows remain visible instead of being cleaned away",
                "later labeling work receives a cleaner admissibility boundary",
            ],
            "stop_criteria": [
                "the map turns into stealth labeling",
                "pending ambiguity is silently erased to force cleaner buckets",
                "the map widens beyond the bounded optical-link cycle",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112aa_cpo_bounded_cohort_map",
            "do_open_v112aa_now": True,
            "selected_parent_line": "v112z_cpo_cycle_absorption",
            "recommended_first_action": "freeze_v112aa_cpo_bounded_cohort_map_v1",
        }
        interpretation = [
            "V1.12AA is the bridge between cycle reconstruction and later labeling review.",
            "Its job is not to add more stories; its job is to make object boundaries and time windows explicit.",
            "Training remains closed while the cohort map is frozen.",
        ]
        return V112AAPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112aa_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AAPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
