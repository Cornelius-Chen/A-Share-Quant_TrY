from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V19PhaseCharterReport:
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


class V19PhaseCharterAnalyzer:
    """Open V1.9 after V1.8C closes with real new breadth evidence."""

    def analyze(
        self,
        *,
        v18c_phase_closure_payload: dict[str, Any],
        v18c_screened_collection_payload: dict[str, Any],
    ) -> V19PhaseCharterReport:
        closure_summary = dict(v18c_phase_closure_payload.get("summary", {}))
        collection_rows = list(v18c_screened_collection_payload.get("collection_rows", []))

        v18c_waiting_ready = bool(closure_summary.get("enter_v18c_waiting_state_now"))
        target_features = sorted(
            {
                str(row.get("feature_name", ""))
                for row in collection_rows
                if row.get("admission_status") == "admit"
            }
        )
        open_v19_now = v18c_waiting_ready and len(target_features) > 0

        charter = {
            "mission": "Re-review whether newly collected bounded breadth evidence changes the promotion judgment for the breadth-target provisional features without promoting or integrating any feature now.",
            "in_scope": [
                "bounded breadth-evidence re-review protocol",
                "per-feature promotion-judgment refresh for breadth targets",
                "updated shortfall ordering after new breadth evidence",
                "phase-level re-review conclusion",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "new collection beyond V1.8C",
                "safe-consumption validation work",
                "cross-pocket or cross-regime validation work",
                "local-model opening",
            ],
            "success_criteria": [
                "freeze a bounded breadth re-review protocol",
                "produce refreshed promotion judgments for the breadth-target features",
                "state whether breadth gaps were materially reduced, unchanged, or resolved",
                "close the phase with a clear follow-up posture",
            ],
            "stop_criteria": [
                "if re-review drifts into direct promotion",
                "if the new breadth evidence is insufficient to support even a bounded judgment refresh",
                "if the phase starts collecting new samples instead of re-reviewing the evidence already collected",
            ],
            "handoff_condition": "After the charter opens, only replay-independent breadth re-review artifacts are allowed until the refreshed promotion posture is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v19_breadth_evidence_rereview"
                if open_v19_now
                else "hold_v19_charter_until_prerequisites_hold"
            ),
            "v18c_waiting_state_present": v18c_waiting_ready,
            "breadth_target_feature_count": len(target_features),
            "target_feature_names": target_features,
            "do_open_v19_now": open_v19_now,
            "recommended_first_action": "freeze_v19_breadth_rereview_protocol_v1",
        }
        interpretation = [
            "V1.8C already produced the first lawful new breadth evidence; the next lawful question is whether that evidence changes promotion judgment.",
            "That makes re-review more appropriate than another design or collection phase.",
            "So V1.9 should open as a bounded breadth-evidence re-review phase, not as a promotion or integration phase.",
        ]
        return V19PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v19_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V19PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
