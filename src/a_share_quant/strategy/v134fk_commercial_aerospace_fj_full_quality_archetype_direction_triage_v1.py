from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fj_commercial_aerospace_full_quality_add_archetype_audit_v1.json"
        )

    def analyze(self) -> V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "retain_full_quality_add_archetype_as_local_supervision_anchor_only"
        triage_rows = [
            {
                "component": "full_quality_add_archetype",
                "status": "retain_as_local_archetype_anchor",
                "rationale": "the strongest local add tier can now be summarized by a simple close-location anchor without losing fidelity inside the current quality ladder",
            },
            {
                "component": "broader_positive_add_promotion",
                "status": "still_blocked",
                "rationale": "a clean archetype inside the strongest local tier does not solve the broader permission-density problem",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "the archetype is useful for supervision readability, not for execution binding",
            },
        ]
        interpretation = [
            "V1.34FK turns the first full-quality add archetype audit into a governance verdict.",
            "The add frontier now has a readable local anchor for its strongest permission tier, but that anchor remains strictly supervision-only.",
        ]
        return V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fk_commercial_aerospace_fj_full_quality_archetype_direction_triage_v1",
                "authoritative_status": status,
                "best_close_loc_15m_threshold": audit["summary"]["best_close_loc_15m_threshold"],
                "best_precision": audit["summary"]["best_precision"],
                "best_coverage": audit["summary"]["best_coverage"],
                "authoritative_rule": (
                    "the add branch should retain the new full-quality archetype as a local supervision anchor while keeping broader promotion and execution blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fk_commercial_aerospace_fj_full_quality_archetype_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
