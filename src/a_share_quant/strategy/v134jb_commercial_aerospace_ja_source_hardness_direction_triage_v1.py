from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1 import (
    V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Report:
        audit = V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "000547",
                "direction": "retain_as_only_hard_anchor_grade_source_and_only_hard_anchor_decoy_counterpanel",
            },
            {
                "component": "603601_and_301306",
                "direction": "retain_as_retained_event_supported_but_non_anchor_source_cases",
            },
            {
                "component": "300342_and_002361",
                "direction": "retain_as_discarded_or_missing_source_cases_not_eligible_for_hard_anchor_promotion",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_because_source_hardness_is_still_single_case",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jb_commercial_aerospace_ja_source_hardness_direction_triage_v1",
            "only_hard_anchor_symbol": audit.summary["only_hard_anchor_symbol"],
            "hard_anchor_grade_source_count": audit.summary["hard_anchor_grade_source_count"],
            "authoritative_status": "retain_source_hardness_stopline_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34JB converts source-hardness classification into direction.",
            "The stack can now say exactly why the current role candidates do not thicken the hard counterpanel: they are lacking anchor-grade source hardness, not merely lagging on price.",
        ]
        return V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jb_commercial_aerospace_ja_source_hardness_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
