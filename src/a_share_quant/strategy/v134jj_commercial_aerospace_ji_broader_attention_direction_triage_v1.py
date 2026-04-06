from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1 import (
    V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer,
)


@dataclass(slots=True)
class V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Report:
        opening = V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "board_local_event_attention_capital_route",
                "direction": "retain_as_frozen_read_only_input",
            },
            {
                "component": "broader_attention_evidence_frontier",
                "direction": "open_protocol_only_and_do_not_claim_live_evidence_yet",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_until_broader_attention_or_new_hard_heat_source_is_retained",
            },
            {
                "component": "concept_purity_business_reference_layer",
                "direction": "defer_until_future_full_a_share_information_is_available",
            },
            {
                "component": "execution_authority",
                "direction": "remain_blocked",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jj_commercial_aerospace_ji_broader_attention_direction_triage_v1",
            "frontier_name": opening.summary["frontier_name"],
            "frontier_state": opening.summary["frontier_state"],
            "execution_blocked": opening.summary["execution_blocked"],
            "authoritative_status": "retain_frozen_local_route_and_only_open_broader_attention_evidence_as_protocol_frontier",
        }
        interpretation = [
            "V1.34JJ converts the broader-attention opening into direction.",
            "The branch sequencing stays clean: freeze the exhausted local inventory, open only the next evidence frontier, and keep promotion plus execution blocked.",
        ]
        return V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jj_commercial_aerospace_ji_broader_attention_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
