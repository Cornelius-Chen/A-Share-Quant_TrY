from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ri_a_share_internal_hot_news_signal_enrichment_audit_v1 import (
    V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Report:
        report = V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "board_signal_row_count": report.summary["board_signal_row_count"],
            "important_queue_row_count": report.summary["important_queue_row_count"],
            "curated_match_count": report.summary["curated_match_count"],
            "matched_board_signal_count": report.summary["matched_board_signal_count"],
            "matched_important_queue_count": report.summary["matched_important_queue_count"],
            "missing_surface_count": report.summary["missing_surface_count"],
            "authoritative_status": "continue_serving_trading_with_explicit_mapping_status_instead_of_implicit_blank_candidate_lists",
        }
        triage_rows = [
            {
                "component": "mapping_enrichment",
                "direction": "attach_board_hit_state_and_beneficiary_mapping_confidence_to_theme-bound_signals",
            },
            {
                "component": "missing_surface_handling",
                "direction": "treat_theme_detected_but_member_surface_missing_as_an_explicit_low-confidence_state_not_as_a_silent_no-op",
            },
            {
                "component": "trading_delivery",
                "direction": "prefer_enriched_board_and_important_views_when_board-specific_routing_is_required",
            },
        ]
        interpretation = [
            "The signal layer now distinguishes missing mapping coverage from genuine broad-market guidance.",
            "The next refinement should expand curated beneficiary coverage or alias coverage rather than hide mapping uncertainty.",
        ]
        return V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rj_a_share_ri_internal_hot_news_signal_enrichment_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
