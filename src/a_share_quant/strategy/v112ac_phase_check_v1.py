from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ACPhaseCheckReport:
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


class V112ACPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        challenge_probe_payload: dict[str, Any],
    ) -> V112ACPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        probe_summary = dict(challenge_probe_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ac_as_review_only_unsupervised_challenge",
            "do_open_v112ac_now": charter_summary.get("do_open_v112ac_now"),
            "supportive_cluster_count": probe_summary.get("supportive_cluster_count"),
            "challenging_cluster_count": probe_summary.get("challenging_cluster_count"),
            "spillover_separation_supported": probe_summary.get("spillover_separation_supported"),
            "pending_quiet_window_supported": probe_summary.get("pending_quiet_window_supported"),
            "allow_auto_role_replacement_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_then_bounded_label_draft_assembly_or_feature-family-review",
        }
        evidence_rows = [
            {
                "evidence_name": "v112ac_unsupervised_role_challenge_probe",
                "actual": {
                    "supportive_cluster_count": probe_summary.get("supportive_cluster_count"),
                    "challenging_cluster_count": probe_summary.get("challenging_cluster_count"),
                    "spillover_separation_supported": probe_summary.get("spillover_separation_supported"),
                    "pending_quiet_window_supported": probe_summary.get("pending_quiet_window_supported"),
                },
                "reading": "The challenger probe can question the manual map, but it still cannot legislate new roles.",
            }
        ]
        interpretation = [
            "V1.12AC is successful if it surfaces supportive and challenging latent structures without crossing governance boundaries.",
            "Formal role replacement, labeling, and training remain closed.",
        ]
        return V112ACPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ac_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ACPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
