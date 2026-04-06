from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ex_commercial_aerospace_add_context_gating_audit_v1.json"
        )

    def analyze(self) -> V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "keep_positive_add_rules_seed_only_and_shift_next_to_point_in_time_add_permission_context_audit"
        triage_rows = [
            {
                "component": "slow_context_gating",
                "status": status,
                "rationale": (
                    "currently available phase, board expectancy, and coarse symbol-role contexts reduce density but still leave broader positive add hits too crowded"
                ),
            },
            {
                "component": "negative_add_governance",
                "status": "retain_as_useful_references",
                "rationale": "failed and blocked add families remain useful bounded governance references and do not need broader promotion to stay informative",
            },
            {
                "component": "intraday_add_execution_authority",
                "status": "still_blocked",
                "rationale": "without a stronger point-in-time add-permission context, broader positive add execution remains unjustified",
            },
        ]
        interpretation = [
            "V1.34EY turns the first context-gating audit into a governance verdict.",
            "The next correct move is to build a point-in-time add-permission context surface, not to keep tuning slow-context combinations.",
        ]
        return V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134ey_commercial_aerospace_ex_context_gating_direction_triage_v1",
                "authoritative_status": status,
                "best_scenario_name": audit["summary"]["best_scenario_name"],
                "best_scenario_non_seed_to_seed_ratio": audit["summary"]["best_scenario_non_seed_to_seed_ratio"],
                "authoritative_rule": (
                    "the intraday-add frontier must keep positive add rules seed-only until a stronger point-in-time permission context can suppress broader shape-only false positives"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ey_commercial_aerospace_ex_context_gating_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
