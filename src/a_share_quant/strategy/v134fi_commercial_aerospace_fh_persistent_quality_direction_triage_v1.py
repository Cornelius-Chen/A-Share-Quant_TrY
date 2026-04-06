from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fh_commercial_aerospace_persistent_permission_quality_audit_v1.json"
        )

    def analyze(self) -> V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "retain_persistent_permission_quality_tiers_as_local_supervision_only"
        triage_rows = [
            {
                "component": "full_quality_persistent_permission",
                "status": "retain_as_strongest_local_add_permission_tier",
                "rationale": "the highest close-location persistent candidates align most closely with full-quality add behavior inside the persistent family surface",
            },
            {
                "component": "bridge_quality_persistent_permission",
                "status": "retain_as_upgrade_watch",
                "rationale": "the bridge tier is where full-like and probe-like persistent candidates still mix, so it should remain a watch layer rather than a clean authorization",
            },
            {
                "component": "probe_quality_persistent_permission",
                "status": "retain_as_lower_acceptance_permission_tier",
                "rationale": "the lower close-location persistent cases still continue, but they should not be overstated as full-quality add permission",
            },
        ]
        interpretation = [
            "V1.34FI turns the first persistent-permission quality audit into a governance verdict.",
            "The add branch now has internal quality structure inside its cleanest local family, but that structure remains supervision-only.",
        ]
        return V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fi_commercial_aerospace_fh_persistent_quality_direction_triage_v1",
                "authoritative_status": status,
                "full_quality_count": audit["summary"]["full_quality_count"],
                "bridge_quality_count": audit["summary"]["bridge_quality_count"],
                "probe_quality_count": audit["summary"]["probe_quality_count"],
                "authoritative_rule": (
                    "persistent add permission now has an internal quality ladder, but it remains a local supervision structure rather than broader permission authority"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fi_commercial_aerospace_fh_persistent_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
