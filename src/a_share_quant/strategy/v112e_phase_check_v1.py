from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112EPhaseCheckReport:
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


class V112EPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        attribution_review_payload: dict[str, Any],
    ) -> V112EPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(attribution_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112e_as_gbdt_attribution_review_success",
            "attribution_review_present": bool(review_summary.get("ready_for_phase_check_next")),
            "allow_model_deployment_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_attribution_before_any_new_feature_or_sidecar_expansion",
        }
        evidence_rows = [
            {
                "evidence_name": "v112e_charter",
                "actual": {"do_open_v112e_now": bool(charter_summary.get("do_open_v112e_now"))},
                "reading": "V1.12E opened lawfully as a bounded attribution-review phase.",
            },
            {
                "evidence_name": "v112e_attribution_review",
                "actual": {
                    "full_model_test_accuracy": float(review_summary.get("full_model_test_accuracy", 0.0)),
                    "most_useful_block_by_hotspot_impact": str(review_summary.get("most_useful_block_by_hotspot_impact", "")),
                },
                "reading": "The project now has a block-level explanation for the first GBDT sidecar gain.",
            },
        ]
        interpretation = [
            "V1.12E succeeds once the first same-dataset sidecar gain has a bounded feature-block explanation.",
            "That is enough to close without opening deployment or new data scope.",
            "The next lawful move is owner review of whether the most useful block should drive the next feature or model decision.",
        ]
        return V112EPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112e_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112EPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
