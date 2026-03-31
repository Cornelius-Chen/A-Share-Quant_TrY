from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BDPhaseCheckReport:
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


class V112BDPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        review_payload: dict[str, Any],
    ) -> V112BDPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112bd_as_market_regime_overlay_feature_review",
            "do_open_v112bd_now": charter_summary.get("do_open_v112bd_now"),
            "overlay_feature_count": review_summary.get("overlay_feature_count"),
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bd_overlay_review",
                "actual": {
                    "overlay_feature_count": review_summary.get("overlay_feature_count"),
                    "overlay_family_count": review_summary.get("overlay_family_count"),
                    "board_style_feature_count": review_summary.get("board_style_feature_count"),
                },
                "reading": "The review is only useful if the project gets an explicit market-regime overlay family without promoting it into core truth.",
            }
        ]
        interpretation = [
            "V1.12BD freezes the market-regime overlay family as a lawful context layer for later experiments.",
            "Formal signal rights remain closed.",
        ]
        return V112BDPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bd_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BDPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
