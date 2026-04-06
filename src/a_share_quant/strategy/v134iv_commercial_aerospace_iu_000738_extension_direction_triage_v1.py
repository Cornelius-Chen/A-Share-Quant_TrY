from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134iu_commercial_aerospace_000738_event_followthrough_extension_audit_v1 import (
    V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Report:
        audit = V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "extension_layer": "event_backing_extension",
                "direction": "promote_as_next_missing_evidence_target",
            },
            {
                "extension_layer": "local_rebound_leadership_extension",
                "direction": "retain_as_current_reason_to_keep_000738_in_watch_status",
            },
            {
                "extension_layer": "followthrough_extension",
                "direction": "retain_as_moderate_supporting_evidence_not_as_persistent_promotion",
            },
            {
                "extension_layer": "capital_true_selection",
                "direction": "continue_blocked_until_000738_gains_retained_event_backing_and thicker downstream support",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134iv_commercial_aerospace_iu_000738_extension_direction_triage_v1",
            "event_backing_present": audit.summary["event_backing_present"],
            "authoritative_status": "retain_000738_watch_and_focus_next_on_event_backing_extension",
        }
        interpretation = [
            "V1.34IV converts the 000738 extension audit into direction.",
            "The next honest step is no longer generic scanning: it is explicitly to search for retained event backing around 000738 while keeping promotion blocked.",
        ]
        return V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iv_commercial_aerospace_iu_000738_extension_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
