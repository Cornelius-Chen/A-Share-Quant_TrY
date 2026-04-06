from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1.json"
        )

    def analyze(self) -> V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "retain_persistent_permission_confirmation_as_local_supervision_only"
        triage_rows = [
            {
                "component": "persistent_permission_confirmation",
                "status": "retain_as_local_confirmation_layer",
                "rationale": (
                    "a simple first-hour continuation gate cleanly separates most persistent permission candidates from fragile and failed counterfactuals"
                ),
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "the confirmation layer sharpens local supervision, but it still does not justify broader positive add promotion or execution binding",
            },
            {
                "component": "fragile_failed_counterfactuals",
                "status": "retain_as_negative_context",
                "rationale": "the add branch still needs the nearby fragile and failed families to keep the permission frontier honest",
            },
        ]
        interpretation = [
            "V1.34FG converts the first persistent-permission confirmation audit into a governance verdict.",
            "The branch now has a credible local continuation confirmation layer, but it remains a supervision object rather than a permission authority.",
        ]
        return V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fg_commercial_aerospace_ff_persistent_confirmation_direction_triage_v1",
                "authoritative_status": status,
                "best_open_to_60m_threshold": audit["summary"]["best_open_to_60m_threshold"],
                "best_continuation_threshold": audit["summary"]["best_continuation_threshold"],
                "best_burst_amount_share_cap": audit["summary"]["best_burst_amount_share_cap"],
                "best_precision": audit["summary"]["best_precision"],
                "best_coverage": audit["summary"]["best_coverage"],
                "authoritative_rule": (
                    "the add frontier should keep the new persistent-permission continuation gate as a local supervision layer while broader positive add promotion remains blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fg_commercial_aerospace_ff_persistent_confirmation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
