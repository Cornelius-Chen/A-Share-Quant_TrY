from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class NextSuspectBatchDesignReport:
    summary: dict[str, Any]
    observed_rows: list[dict[str, Any]]
    missing_archetypes: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "observed_rows": self.observed_rows,
            "missing_archetypes": self.missing_archetypes,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class NextSuspectBatchDesignAnalyzer:
    """Translate current closed-slice geography into the next suspect-batch design rules."""

    def analyze(
        self,
        *,
        context_audit: dict[str, Any],
        continuation_readiness: dict[str, Any],
        specialist_alpha: dict[str, Any],
    ) -> NextSuspectBatchDesignReport:
        slice_rows = list(context_audit.get("slice_rows", []))
        observed_rows: list[dict[str, Any]] = []
        observed_signatures: set[tuple[str, str, str]] = set()

        for row in slice_rows:
            tags = {str(tag) for tag in row.get("context_tags", [])}
            theme_bucket = "theme_loaded" if "theme_loaded" in tags else "theme_light"
            turnover_bucket = (
                "concentrated_turnover"
                if "concentrated_turnover" in tags
                else "balanced_turnover"
            )
            sector_bucket = "broad_sector" if "broad_sector" in tags else "narrow_sector"
            observed_signatures.add((theme_bucket, turnover_bucket, sector_bucket))
            observed_rows.append(
                {
                    "dataset_name": row.get("dataset_name"),
                    "slice_name": row.get("slice_name"),
                    "slice_role": row.get("slice_role"),
                    "theme_bucket": theme_bucket,
                    "turnover_bucket": turnover_bucket,
                    "sector_bucket": sector_bucket,
                    "context_tags": row.get("context_tags", []),
                }
            )

        candidate_grid = [
            ("theme_loaded", "balanced_turnover", "broad_sector"),
            ("theme_loaded", "balanced_turnover", "narrow_sector"),
            ("theme_light", "balanced_turnover", "narrow_sector"),
            ("theme_light", "concentrated_turnover", "broad_sector"),
        ]
        specialist_opportunity_count = int(
            sum(
                int(row.get("opportunity_count", 0))
                for row in specialist_alpha.get("specialist_summaries", [])
            )
        )
        missing_archetypes: list[dict[str, Any]] = []
        for theme_bucket, turnover_bucket, sector_bucket in candidate_grid:
            if (theme_bucket, turnover_bucket, sector_bucket) in observed_signatures:
                continue
            if theme_bucket == "theme_loaded" and turnover_bucket == "balanced_turnover":
                rationale = "Tests whether specialist edges survive when concept load stays high but turnover is not dominated by one name."
            elif theme_bucket == "theme_light" and turnover_bucket == "concentrated_turnover":
                rationale = "Stresses low-theme slices where one or two names still dominate turnover but sector structure is broader."
            else:
                rationale = "Adds an underrepresented sector/theme interaction archetype missing from the current closed slices."
            missing_archetypes.append(
                {
                    "theme_bucket": theme_bucket,
                    "turnover_bucket": turnover_bucket,
                    "sector_bucket": sector_bucket,
                    "priority": len(missing_archetypes) + 1,
                    "rationale": rationale,
                }
            )

        summary = {
            "current_loop_paused": bool(
                continuation_readiness.get("summary", {}).get("do_continue_current_specialist_loop")
                is False
            ),
            "observed_closed_slice_count": len(observed_rows),
            "specialist_opportunity_count": specialist_opportunity_count,
            "top_specialist_by_opportunity_count": specialist_alpha.get("summary", {}).get(
                "top_specialist_by_opportunity_count"
            ),
            "missing_archetype_count": len(missing_archetypes),
            "recommended_next_batch_name": "market_research_v2_seed",
            "recommended_batch_posture": "expand_by_missing_context_archetypes",
        }
        interpretation = [
            "Once the current specialist loop is paused, the next batch should not be a random size expansion.",
            "The new suspect batch should target context archetypes that are missing from the current closed-slice geography.",
            "This keeps the next batch tied to decision-boundary gaps rather than general sample hunger.",
        ]
        return NextSuspectBatchDesignReport(
            summary=summary,
            observed_rows=observed_rows,
            missing_archetypes=missing_archetypes,
            interpretation=interpretation,
        )


def write_next_suspect_batch_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: NextSuspectBatchDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
