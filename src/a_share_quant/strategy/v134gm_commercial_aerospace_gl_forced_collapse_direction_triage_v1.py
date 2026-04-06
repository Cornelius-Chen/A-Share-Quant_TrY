from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1.json"
        )

    def analyze(self) -> V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "forced_collapse_surrogate",
                "status": "retain_as_reset_only",
                "rationale": "under a forced one-slot local reading, reset remains the only slot with a stronger combined allocation-plus-quality claim",
            },
            {
                "component": "continuation_slot",
                "status": "retain_as_companion_only",
                "rationale": "continuation keeps a local early-impulse edge but does not carry the stronger forced-collapse claim",
            },
            {
                "component": "portable_single_slot_template",
                "status": "still_blocked",
                "rationale": "forced collapse on one dual-slot day is still not evidence of an observed portable single-slot state",
            },
            {
                "component": "execution_single_slot_rule",
                "status": "still_blocked",
                "rationale": "the branch still lacks an observed execution-safe one-slot template",
            },
        ]
        interpretation = [
            "V1.34GM turns the forced single-slot collapse audit into the current governance verdict.",
            "The branch may retain reset as the stronger local surrogate under forced collapse, but that does not unlock a portable single-slot rule.",
        ]
        return V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gm_commercial_aerospace_gl_forced_collapse_direction_triage_v1",
                "authoritative_status": (
                    "retain_reset_slot_as_forced_collapse_surrogate_and_keep_single_slot_promotion_blocked"
                ),
                "preferred_surrogate_slot": audit["summary"]["preferred_surrogate_slot"],
                "preferred_surrogate_symbol": audit["summary"]["preferred_surrogate_symbol"],
                "reset_higher_metric_count": audit["summary"]["reset_higher_metric_count"],
                "continuation_higher_metric_count": audit["summary"]["continuation_higher_metric_count"],
                "authoritative_rule": (
                    "forced-collapse preference may favor reset locally, but single-slot fallback remains unobserved and non-portable"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gm_commercial_aerospace_gl_forced_collapse_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
