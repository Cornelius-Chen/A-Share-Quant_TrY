from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Report:
    summary: dict[str, Any]
    gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "gap_rows": self.gap_rows,
            "interpretation": self.interpretation,
        }


class V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_carrier_grade_evidence_gap_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Report:
        separation = self._load_json(
            "reports/analysis/v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        )
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )

        carrier_candidates = [
            row for row in separation["separated_rows"] if row["separated_role"] == "event_backed_attention_carrier_candidate"
        ]
        hard_anchor_rows = [
            row for row in event_attention["registry_rows"] if row["supervision_label"] == "attention_anchor"
        ]
        hard_decoy_rows = [
            row for row in event_attention["registry_rows"] if row["supervision_label"] == "attention_decoy"
        ]

        gap_rows = [
            {
                "gap_name": "second_event_backed_carrier_case_missing",
                "status": "active_gap",
                "evidence": len(carrier_candidates),
                "required_minimum": 2,
                "reading": "only one event-backed carrier-grade soft case exists, so there is no second case to compare against before promoting true selection",
            },
            {
                "gap_name": "anchor_decoy_counterpanel_too_thin",
                "status": "active_gap",
                "evidence": len(hard_anchor_rows),
                "required_minimum": 2,
                "reading": "the role layer currently has only one hard anchor/decoy case, so divergence patterns are still under-specified",
            },
            {
                "gap_name": "carrier_followthrough_not_yet_labeled",
                "status": "active_gap",
                "evidence": "unlabeled",
                "required_minimum": "first_followthrough_registry",
                "reading": "the current role layer separates carrier/follow/concentration, but it has not yet built a dedicated followthrough label surface",
            },
            {
                "gap_name": "board_event_alignment_not_yet_explicit",
                "status": "active_gap",
                "evidence": "partial",
                "required_minimum": "event_to_board_alignment_panel",
                "reading": "event trigger validity exists, but the degree of board-level alignment after event visibility is not yet scored as its own supervision object",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(gap_rows[0].keys()))
            writer.writeheader()
            writer.writerows(gap_rows)

        summary = {
            "acceptance_posture": "freeze_v134ic_commercial_aerospace_carrier_grade_evidence_gap_audit_v1",
            "event_backed_attention_carrier_count": len(carrier_candidates),
            "hard_anchor_case_count": len(hard_anchor_rows),
            "hard_decoy_case_count": len(hard_decoy_rows),
            "active_gap_count": sum(1 for row in gap_rows if row["status"] == "active_gap"),
            "gap_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "capital_true_selection remains blocked for explicit reasons: the current layer lacks a second event-backed carrier case, lacks a thicker hard anchor/decoy counterpanel, and still has no dedicated followthrough surface",
        }
        interpretation = [
            "V1.34IC turns the carrier-grade blocker into explicit gaps instead of a vague feeling that the evidence is not enough.",
            "This matters because the next work can now be driven by named missing evidence rather than by subjective hesitation.",
        ]
        return V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Report(
            summary=summary,
            gap_rows=gap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ic_commercial_aerospace_carrier_grade_evidence_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
