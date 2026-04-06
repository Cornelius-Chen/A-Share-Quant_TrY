from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ez_commercial_aerospace_add_permission_context_audit_v1.json"
        )

    def analyze(self) -> V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "keep_positive_add_rules_seed_only_but_retain_point_in_time_permission_clues_as_local_supervision"
        triage_rows = [
            {
                "component": "positive_add_broader_promotion",
                "status": "still_blocked",
                "rationale": (
                    "point-in-time quantity-price moderation improves density, but broader positive add hits remain too crowded to authorize promotion"
                ),
            },
            {
                "component": "narrow_high_confidence_permission_clue",
                "status": "retain_as_local_supervision",
                "rationale": (
                    "unlock-worthy, high-role symbols with contained first-15m amount usage form the cleanest current add-permission clue"
                ),
            },
            {
                "component": "reduce_volume_price_appendix",
                "status": "refresh_as_governance_only",
                "rationale": "the reduce branch should carry its existing volume-price confirmation and local veto logic explicitly inside the frozen handoff package",
            },
        ]
        interpretation = [
            "V1.34FA turns the first add-focused point-in-time quantity-price audit into the next governance verdict.",
            "The branch should not broaden positive add promotion yet, but it now has a credible local permission clue worth keeping as supervision.",
        ]
        return V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fa_commercial_aerospace_ez_add_permission_direction_triage_v1",
                "authoritative_status": status,
                "best_point_in_time_broad_scenario": audit["summary"]["best_point_in_time_broad_scenario"],
                "best_point_in_time_broad_ratio": audit["summary"]["best_point_in_time_broad_ratio"],
                "best_high_confidence_scenario": audit["summary"]["best_high_confidence_scenario"],
                "best_high_confidence_ratio": audit["summary"]["best_high_confidence_ratio"],
                "authoritative_rule": (
                    "intraday add should keep positive rules seed-only, while retaining point-in-time quantity-price permission clues as local supervision inputs"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fa_commercial_aerospace_ez_add_permission_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
