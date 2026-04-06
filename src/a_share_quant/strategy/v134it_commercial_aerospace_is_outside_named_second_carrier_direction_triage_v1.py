from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1 import (
    V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Report:
        audit = V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "supervision_role": "outside_named_local_leadership_second_carrier_watch",
                "direction": "promote_as_next_event_backing_and_followthrough_extension_target",
            },
            {
                "supervision_role": "current_primary_event_backed_carrier_case",
                "direction": "retain_as_primary_reference_not_as_sufficient_peer_stack",
            },
            {
                "supervision_role": "capital_true_selection",
                "direction": "continue_blocked_until_outside_named_watch_gains_retained_event_backing_and downstream role evidence",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134it_commercial_aerospace_is_outside_named_second_carrier_direction_triage_v1",
            "outside_named_watch_count": audit.summary["outside_named_watch_count"],
            "authoritative_status": "retain_000738_as_next_outside_named_second_carrier_watch_without_promoting_true_selection",
        }
        interpretation = [
            "V1.34IT converts the outside-named watch into direction.",
            "The next honest move is to extend event-backing and followthrough labeling to 000738 rather than to skip directly to promotion.",
        ]
        return V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134it_commercial_aerospace_is_outside_named_second_carrier_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
