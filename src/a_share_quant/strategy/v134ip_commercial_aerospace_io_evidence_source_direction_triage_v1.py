from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134io_commercial_aerospace_true_selection_evidence_source_audit_v1 import (
    V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Report:
        audit = V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "next_target": "expanded_symbol_universe",
                "direction": "promote_as_next_carrier_search_surface",
            },
            {
                "next_target": "attention_heat_evidence_expansion",
                "direction": "promote_as_next_counterpanel_thickening_surface",
            },
            {
                "next_target": "current_named_universe_retuning",
                "direction": "deprioritize_as_locally_exhausted",
            },
            {
                "next_target": "capital_true_selection",
                "direction": "continue_blocked_until_new_evidence_sources_expand_the_comparison_stack",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ip_commercial_aerospace_io_evidence_source_direction_triage_v1",
            "current_local_route_exhausted": audit.summary["current_local_route_exhausted"],
            "authoritative_status": "retain_true_selection_block_and_shift_next_work_toward_evidence_source_expansion",
        }
        interpretation = [
            "V1.34IP converts evidence-source exhaustion into direction.",
            "The main point is to stop retuning a locally exhausted set and start seeking the missing comparison evidence from broader symbol and attention surfaces.",
        ]
        return V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ip_commercial_aerospace_io_evidence_source_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
