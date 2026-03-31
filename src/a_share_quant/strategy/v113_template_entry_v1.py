from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113TemplateEntryReport:
    summary: dict[str, Any]
    template_family_rows: list[dict[str, Any]]
    seed_archetype_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "template_family_rows": self.template_family_rows,
            "seed_archetype_rows": self.seed_archetype_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113TemplateEntryAnalyzer:
    def analyze(self, *, phase_charter_payload: dict[str, Any]) -> V113TemplateEntryReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_template_entry_next")):
            raise ValueError("V1.13 requires an open phase charter.")

        template_family_rows = [
            {
                "template_family_name": "earnings_transmission_carry",
                "current_posture": "already_has_bounded_single_cycle_pilot_but_not_current_highest_leverage_next_step",
                "reading": "Still valid, but the current best leverage is no longer to deepen the same narrow pocket immediately.",
            },
            {
                "template_family_name": "expectation_cycle_carry",
                "current_posture": "important_but_not_first_reentry_target_now",
                "reading": "Useful later, but not the clearest next line for the current A-share carry grammar reset.",
            },
            {
                "template_family_name": "theme_diffusion_carry",
                "current_posture": "selected_as_primary_next_template_line",
                "reading": "Chosen because it better matches the highest-frequency A-share carry alpha shape: diffusion, catch-up, relay, and decay.",
            },
        ]
        seed_archetype_rows = [
            {
                "archetype_name": "commercial_space_mainline",
                "template_role": "theme_diffusion_seed",
                "reading": "Policy/theme-led mainline suitable for diffusion, catch-up, and relay-state study.",
            },
            {
                "archetype_name": "stablecoin_theme_cycle",
                "template_role": "theme_diffusion_seed",
                "reading": "A fast-expanding theme cycle suitable for cross-day breadth and laggard-activation study.",
            },
            {
                "archetype_name": "low_altitude_economy_cycle",
                "template_role": "theme_diffusion_seed",
                "reading": "A-share thematic diffusion example with policy linkage and layered stock-role spread.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v113_template_entry_v1",
            "selected_template_family": "theme_diffusion_carry",
            "seed_archetype_count": len(seed_archetype_rows),
            "schema_first_posture": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13 formally changes the effort frontier from local high-level consolidation refinement to a broader carry grammar line.",
            "theme_diffusion_carry is selected because it better matches the main A-share alpha mechanism discussed in owner review.",
            "The next lawful move should still be schema-first, not model-first or execution-first.",
        ]
        return V113TemplateEntryReport(
            summary=summary,
            template_family_rows=template_family_rows,
            seed_archetype_rows=seed_archetype_rows,
            interpretation=interpretation,
        )


def write_v113_template_entry_report(*, reports_dir: Path, report_name: str, result: V113TemplateEntryReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
