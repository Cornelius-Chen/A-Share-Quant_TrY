from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jg_commercial_aerospace_event_attention_capital_local_handoff_package_v1 import (
    V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer,
)


@dataclass(slots=True)
class V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Report:
        handoff = V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "board_local_event_attention_capital_route",
                "direction": "freeze_mainline_and_do_not_reopen_inside_same_local_inventory",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_until_new_hard_heat_source_or_broader_attention_evidence_exists",
            },
            {
                "component": "future_progress_source",
                "direction": "treat_as_future_evidence_expansion_only",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jh_commercial_aerospace_jg_local_handoff_direction_triage_v1",
            "future_handoff_ready": handoff.summary["future_handoff_ready"],
            "capital_true_selection_blocked": handoff.summary["capital_true_selection_blocked"],
            "authoritative_status": "freeze_board_local_event_attention_capital_route_and_wait_for_future_evidence_shift",
        }
        interpretation = [
            "V1.34JH turns the local handoff package into direction.",
            "The branch should now be treated the same way earlier frozen lines were treated: preserve the learned stack and refuse to drift inside the same evidence inventory.",
        ]
        return V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jh_commercial_aerospace_jg_local_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
