from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fl_commercial_aerospace_full_quality_module_portability_audit_v1.json"
        )

    def analyze(self) -> V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "keep_full_quality_add_archetype_local_only_and_block_module_promotion"
        triage_rows = [
            {
                "component": "local_full_quality_archetype",
                "status": "retain_as_local_anchor",
                "rationale": "the archetype is useful and clean inside the local persistent-quality ladder",
            },
            {
                "component": "portable_high_confidence_module",
                "status": "not_yet_authorized",
                "rationale": "even the strongest portable-looking scenario still retains too many non-seed sessions relative to the number of seed cases kept",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "the archetype remains local supervision only; portability failure keeps module promotion and execution blocked",
            },
        ]
        interpretation = [
            "V1.34FM turns the first full-quality module portability audit into a governance verdict.",
            "The add branch now knows that its strongest archetype is real but still local: it should not be mistaken for a portable module.",
        ]
        return V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fm_commercial_aerospace_fl_module_portability_direction_triage_v1",
                "authoritative_status": status,
                "best_scenario_name": audit["summary"]["best_scenario_name"],
                "best_scenario_non_seed_to_seed_ratio": audit["summary"]["best_scenario_non_seed_to_seed_ratio"],
                "best_scenario_seed_kept_count": audit["summary"]["best_scenario_seed_kept_count"],
                "best_scenario_non_seed_kept_count": audit["summary"]["best_scenario_non_seed_kept_count"],
                "authoritative_rule": (
                    "the strongest local add archetype remains local; it should not be promoted into a broader module until portability improves materially"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fm_commercial_aerospace_fl_module_portability_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
