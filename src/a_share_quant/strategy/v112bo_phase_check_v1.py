from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BOPhaseCheckReport:
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


class V112BOPhaseCheckAnalyzer:
    def analyze(self, *, overlay_review_payload: dict[str, Any]) -> V112BOPhaseCheckReport:
        summary_in = dict(overlay_review_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BO phase check requires the completed overlay review.")

        summary = {
            "acceptance_posture": "keep_v112bo_as_cpo_internal_maturity_overlay_review",
            "do_open_v112bo_now": True,
            "overlay_feature_count": int(summary_in.get("overlay_feature_count", 0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bo_overlay_review",
                "actual": {
                    "overlay_feature_count": summary_in.get("overlay_feature_count"),
                    "recommended_next_posture": summary_in.get("recommended_next_posture"),
                },
                "reading": "The phase is only useful if internal maturity is frozen as a distinct overlay family instead of getting mixed into regime or role truth.",
            }
        ]
        interpretation = [
            "V1.12BO is valid because it isolates the internal maturity layer the BL regime experiment failed to recover by itself.",
        ]
        return V112BOPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bo_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BOPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
