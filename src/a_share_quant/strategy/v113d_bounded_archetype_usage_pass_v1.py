from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113DBoundedArchetypeUsagePassReport:
    summary: dict[str, Any]
    archetype_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "archetype_review_rows": self.archetype_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113DBoundedArchetypeUsagePassAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        template_entry_payload: dict[str, Any],
        state_usage_review_payload: dict[str, Any],
    ) -> V113DBoundedArchetypeUsagePassReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_archetype_usage_pass_next")):
            raise ValueError("V1.13D requires an open bounded archetype usage pass charter.")

        usage_summary = dict(state_usage_review_payload.get("summary", {}))
        if int(usage_summary.get("drivers_allowed_for_schema_review_only", 0)) != 4:
            raise ValueError("V1.13D requires the four-driver schema-review-only quartet from V1.13C.")

        seed_rows = list(template_entry_payload.get("seed_archetype_rows", []))
        if len(seed_rows) != 3:
            raise ValueError("V1.13D expects exactly three frozen seed archetypes from V1.13.")

        archetype_map = {
            "commercial_space_mainline": {
                "state_role_clarity": "high",
                "strength_clarity": "high",
                "driver_overreach_risk": "medium",
                "review_disposition": "preserve_as_clean_template_review_asset",
                "reading": (
                    "This archetype fits the grammar cleanly: policy and event resonance can be used without immediately collapsing "
                    "role, strength, and driver into one bucket."
                ),
            },
            "stablecoin_theme_cycle": {
                "state_role_clarity": "medium",
                "strength_clarity": "medium",
                "driver_overreach_risk": "high",
                "review_disposition": "preserve_as_fast_cycle_review_asset_but_not_template_core_yet",
                "reading": (
                    "Useful for fast diffusion review, but event resonance and narrative spillover risk over-dominating the archetype."
                ),
            },
            "low_altitude_economy_cycle": {
                "state_role_clarity": "medium",
                "strength_clarity": "medium",
                "driver_overreach_risk": "medium",
                "review_disposition": "preserve_as_policy_industry_review_asset_with_mapping_noise",
                "reading": (
                    "The grammar works, but mapping activation and policy-story overlap create more role/driver mixing than the strongest seed."
                ),
            },
        }

        archetype_review_rows: list[dict[str, Any]] = []
        clean_asset_count = 0
        for row in seed_rows:
            name = str(row.get("archetype_name", ""))
            derived = archetype_map[name]
            if derived["review_disposition"] == "preserve_as_clean_template_review_asset":
                clean_asset_count += 1
            archetype_review_rows.append(
                {
                    "archetype_name": name,
                    "state_role_clarity": derived["state_role_clarity"],
                    "strength_clarity": derived["strength_clarity"],
                    "driver_overreach_risk": derived["driver_overreach_risk"],
                    "review_disposition": derived["review_disposition"],
                    "reading": derived["reading"],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113d_bounded_archetype_usage_pass_v1",
            "archetype_count_reviewed": len(archetype_review_rows),
            "clean_template_review_asset_count": clean_asset_count,
            "formal_template_promotion_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13D is a template-usage review, not an execution or feature phase.",
            "The grammar appears archetype-usable, but not all archetypes are equally clean.",
            "The result is sufficient to preserve one strong core archetype and two bounded review assets without over-promoting them.",
        ]
        return V113DBoundedArchetypeUsagePassReport(
            summary=summary,
            archetype_review_rows=archetype_review_rows,
            interpretation=interpretation,
        )


def write_v113d_bounded_archetype_usage_pass_report(
    *, reports_dir: Path, report_name: str, result: V113DBoundedArchetypeUsagePassReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
