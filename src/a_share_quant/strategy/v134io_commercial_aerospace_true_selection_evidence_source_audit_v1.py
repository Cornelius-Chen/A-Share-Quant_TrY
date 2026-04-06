from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Report:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_true_selection_evidence_sources_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Report:
        readiness = self._load_json(
            "reports/analysis/v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1.json"
        )
        second_carrier = self._load_json(
            "reports/analysis/v134ie_commercial_aerospace_second_carrier_case_search_audit_v1.json"
        )
        counterpanel = self._load_json(
            "reports/analysis/v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1.json"
        )

        source_rows = [
            {
                "missing_gap": "second_event_backed_carrier_case",
                "current_local_status": "not_found_inside_current_named_universe",
                "next_evidence_source": "expanded_symbol_universe",
                "source_reason": "the current named set already searched five focal symbols and still produced only one primary carrier-grade case",
            },
            {
                "missing_gap": "anchor_decoy_counterpanel",
                "current_local_status": "hard_panel_still_singleton",
                "next_evidence_source": "attention_heat_evidence_expansion",
                "source_reason": "soft decoy-like names exist, but the current local panel still has only one hard anchor-decoy reference and lacks thicker attention evidence",
            },
            {
                "missing_gap": "capital_true_selection",
                "current_local_status": "blocked_after_partial_gap_closure",
                "next_evidence_source": "joint_universe_plus_attention_expansion",
                "source_reason": "followthrough and board-event alignment are now explicit, so the remaining progress can no longer come from local shape refinement alone",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
            writer.writeheader()
            writer.writerows(source_rows)

        summary = {
            "acceptance_posture": "freeze_v134io_commercial_aerospace_true_selection_evidence_source_audit_v1",
            "remaining_hard_gap_count": readiness["summary"]["remaining_hard_gap_count"],
            "searched_symbol_count": second_carrier["summary"]["searched_symbol_count"],
            "current_hard_counterpanel_count": counterpanel["summary"]["current_hard_counterpanel_count"],
            "current_local_route_exhausted": True,
            "evidence_source_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the next true-selection progress no longer comes from retuning the current local named set; it requires evidence-source expansion, especially broader symbol coverage and thicker attention-heat evidence",
        }
        interpretation = [
            "V1.34IO turns the remaining blocker stack into an evidence-source problem instead of pretending more local refinement will solve it.",
            "The implication is procedural: stay honest about local exhaustion and route the next search toward broader symbol and attention evidence rather than toward synthetic promotion.",
        ]
        return V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Report(
            summary=summary,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134io_commercial_aerospace_true_selection_evidence_source_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
