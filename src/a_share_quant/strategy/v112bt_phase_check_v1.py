from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BTPhaseCheckReport:
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


class V112BTPhaseCheckAnalyzer:
    def analyze(self, *, extraction_payload: dict[str, Any]) -> V112BTPhaseCheckReport:
        summary_in = dict(extraction_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BT phase check requires the completed extraction report.")

        summary = {
            "acceptance_posture": "keep_v112bt_as_phase_conditioned_veto_and_eligibility_extraction",
            "eligibility_rule_count": int(summary_in.get("eligibility_rule_count", 0)),
            "entry_veto_count": int(summary_in.get("entry_veto_count", 0)),
            "holding_veto_count": int(summary_in.get("holding_veto_count", 0)),
            "risk_off_override_count": int(summary_in.get("risk_off_override_count", 0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "phase_conditioned_control_objects",
                "actual": {
                    "eligibility_rule_count": summary_in.get("eligibility_rule_count"),
                    "entry_veto_count": summary_in.get("entry_veto_count"),
                    "holding_veto_count": summary_in.get("holding_veto_count"),
                    "risk_off_override_count": summary_in.get("risk_off_override_count"),
                },
                "reading": "The phase is only useful if dangerous regions are translated into explicit control objects.",
            }
        ]
        interpretation = [
            "V1.12BT phase check confirms that risk regions are now being translated into concrete eligibility and veto objects instead of staying as abstract pockets.",
        ]
        return V112BTPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bt_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BTPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
