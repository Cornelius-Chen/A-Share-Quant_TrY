from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.feed_path = (
            repo_root / "reports" / "analysis" / "v134el_commercial_aerospace_intraday_add_point_in_time_seed_feed_v1.json"
        )

    def analyze(self) -> V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Report:
        feed = json.loads(self.feed_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "build_v134em_commercial_aerospace_el_add_seed_feed_direction_triage_v1",
            "authoritative_status": "retain_intraday_add_point_in_time_seed_feed_and_shift_next_to_add_tiered_label_specification",
            "seed_session_count": feed["summary"]["seed_session_count"],
            "feed_row_count": feed["summary"]["feed_row_count"],
            "authoritative_rule": "after the add registry exists, the next justified step is to translate point-in-time seed feeds into add tier labels",
        }
        triage_rows = [
            {
                "component": "allowed_add_seed",
                "status": "ready_for_tier_label_translation",
                "rationale": "positive add seeds now have minute-lawful visibility and can support early add-tier specification",
            },
            {
                "component": "failed_add_seed",
                "status": "retain_as_negative_supervision",
                "rationale": "the failed add cases now have lawful seed feeds and should remain explicit negative evidence",
            },
            {
                "component": "blocked_add_seed",
                "status": "retain_as_veto_context",
                "rationale": "board-level veto states are now carried inside the feed and should stay upstream of later add logic",
            },
        ]
        interpretation = [
            "V1.34EM converts the add point-in-time feed into a direction judgment for the still-young add frontier.",
            "The next justified artifact is an add tiered label specification, not execution authority and not all-session expansion.",
        ]
        return V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134em_commercial_aerospace_el_add_seed_feed_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
