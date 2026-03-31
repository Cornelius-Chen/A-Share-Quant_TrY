from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APilotObjectPoolReport:
    summary: dict[str, Any]
    object_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "object_rows": self.object_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112APilotObjectPoolAnalyzer:
    """Freeze the first bounded object pool for the optical-link upcycle pilot."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
    ) -> V112APilotObjectPoolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112a_now")):
            raise ValueError("V1.12A must be open before pilot object pool freeze.")

        object_rows = [
            {
                "symbol": "300502",
                "name": "新易盛",
                "pool_role_guess": "core_beta_beneficiary",
                "cycle_fit": "high",
                "local_evidence_status": "repo_seen",
                "cycle_window_status": "owner_review_needed",
                "missing_object_override_allowed": True,
            },
            {
                "symbol": "300308",
                "name": "中际旭创",
                "pool_role_guess": "leader_or_core_beneficiary",
                "cycle_fit": "high",
                "local_evidence_status": "owner_seeded_name",
                "cycle_window_status": "owner_review_needed",
                "missing_object_override_allowed": True,
            },
            {
                "symbol": "300394",
                "name": "天孚通信",
                "pool_role_guess": "mid_core_component_beneficiary",
                "cycle_fit": "high",
                "local_evidence_status": "owner_seeded_name",
                "cycle_window_status": "owner_review_needed",
                "missing_object_override_allowed": True,
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v112a_pilot_object_pool_v1",
            "pilot_object_count": len(object_rows),
            "repo_seen_object_count": sum(1 for row in object_rows if row["local_evidence_status"] == "repo_seen"),
            "owner_seeded_object_count": sum(1 for row in object_rows if row["local_evidence_status"] == "owner_seeded_name"),
            "ready_for_label_review_sheet_next": True,
        }
        interpretation = [
            "The first pilot object pool stays intentionally small so the owner can inspect every object and correct omissions.",
            "Only one object is already present inside repo evidence; the other two are owner-seeded expansion objects and therefore explicitly marked as requiring review.",
            "This pool is a bounded draft, not a final truth set.",
        ]
        return V112APilotObjectPoolReport(summary=summary, object_rows=object_rows, interpretation=interpretation)


def write_v112a_pilot_object_pool_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APilotObjectPoolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
