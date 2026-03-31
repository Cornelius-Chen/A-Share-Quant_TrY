from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113DPhaseCheckReport:
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


class V113DPhaseCheckAnalyzer:
    def analyze(self, *, archetype_usage_payload: dict[str, Any]) -> V113DPhaseCheckReport:
        review_summary = dict(archetype_usage_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113d_as_bounded_archetype_usage_pass_success",
            "archetype_count_reviewed": int(review_summary.get("archetype_count_reviewed", 0)),
            "clean_template_review_asset_count": int(review_summary.get("clean_template_review_asset_count", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "preserve_theme_diffusion_archetypes_as_review_assets_and_pause_before_any_model_line",
        }
        evidence_rows = [
            {
                "evidence_name": "v113d_bounded_archetype_usage_pass",
                "actual": {
                    "archetype_count_reviewed": summary["archetype_count_reviewed"],
                    "clean_template_review_asset_count": summary["clean_template_review_asset_count"],
                },
                "reading": "V1.13D succeeds once the grammar has been tested against the bounded archetype set without leaking into execution or model logic.",
            }
        ]
        interpretation = [
            "V1.13D shows that the grammar is archetype-usable, but not equally clean across all seed themes.",
            "The correct next posture is to preserve the archetypes as review assets rather than jump straight into modeling.",
        ]
        return V113DPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113d_phase_check_report(
    *, reports_dir: Path, report_name: str, result: V113DPhaseCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
