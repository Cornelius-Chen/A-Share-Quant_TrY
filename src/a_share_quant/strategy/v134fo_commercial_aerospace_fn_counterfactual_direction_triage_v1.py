from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134fn_commercial_aerospace_full_quality_module_counterfactual_audit_v1.json"
        )

    def analyze(self) -> V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))

        authoritative_status = (
            "keep_add_portability_blocked_and_shift_next_to_day_level_selection_authority_supervision"
        )
        triage_rows = [
            {
                "component": "local_full_quality_archetype",
                "status": "retain_as_local_anchor",
                "rationale": "the best local full-quality add object is still valid inside the local permission hierarchy",
            },
            {
                "component": "portable_module_promotion",
                "status": "still_blocked",
                "rationale": "the residual non-seed hits are displaced or late-echo counterfactuals, so portability still fails even after local shape and burst moderation are strong",
            },
            {
                "component": "next_supervision_direction",
                "status": "shift_to_day_level_selection_authority",
                "rationale": "the remaining blocker is no longer local shape; it is whether the branch can justify same-day symbol selection and no-order-day counterfactual promotion",
            },
        ]
        interpretation = [
            "V1.34FO turns the counterfactual audit into a governance verdict for the add frontier.",
            "The add branch should stop trying to widen its strongest local module with more local shape tweaks and instead study the missing day-level selection authority that separates real add permission from displaced or late-echo counterfactuals.",
        ]
        return V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fo_commercial_aerospace_fn_counterfactual_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "scenario_name": audit["summary"]["scenario_name"],
                "counterfactual_count": audit["summary"]["counterfactual_count"],
                "selection_displacement_counterfactual_count": audit["summary"][
                    "selection_displacement_counterfactual_count"
                ],
                "no_order_day_post_seed_echo_count": audit["summary"]["no_order_day_post_seed_echo_count"],
                "authoritative_rule": (
                    "the current add blocker has shifted from local shape to day-level selection authority; broader promotion stays blocked until that layer is understood"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fo_commercial_aerospace_fn_counterfactual_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
