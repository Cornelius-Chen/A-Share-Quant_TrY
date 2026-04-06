from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Report:
    summary: dict[str, Any]
    gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "gap_rows": self.gap_rows,
            "interpretation": self.interpretation,
        }


class V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_capital_true_selection_readiness_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Report:
        second_carrier = self._load_json(
            "reports/analysis/v134ie_commercial_aerospace_second_carrier_case_search_audit_v1.json"
        )
        counterpanel = self._load_json(
            "reports/analysis/v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1.json"
        )
        followthrough = self._load_json(
            "reports/analysis/v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1.json"
        )
        board_alignment = self._load_json(
            "reports/analysis/v134ik_commercial_aerospace_board_event_alignment_supervision_audit_v1.json"
        )

        gap_rows = [
            {
                "gap_name": "second_event_backed_carrier_case",
                "current_status": "still_missing",
                "blocker_strength": "hard",
                "evidence": f"primary_carrier_case_count={second_carrier['summary']['current_primary_carrier_case_count']}; second_carrier_case_found={second_carrier['summary']['second_carrier_case_found']}",
                "promotion_effect": "blocks capital_true_selection because carrier evidence still sits on a single primary case",
            },
            {
                "gap_name": "anchor_decoy_counterpanel",
                "current_status": "still_thin",
                "blocker_strength": "hard",
                "evidence": f"current_hard_counterpanel_count={counterpanel['summary']['current_hard_counterpanel_count']}; second_hard_counterpanel_found={counterpanel['summary']['second_hard_counterpanel_found']}",
                "promotion_effect": "blocks capital_true_selection because hard attention contrast still depends on one retained anchor-decoy reference",
            },
            {
                "gap_name": "symbol_followthrough_surface",
                "current_status": "explicit_layer_now_present",
                "blocker_strength": "supporting_only",
                "evidence": f"persistent_followthrough_count={followthrough['summary']['persistent_followthrough_count']}; moderate_followthrough_count={followthrough['summary']['moderate_followthrough_count']}",
                "promotion_effect": "helps discriminate persistence but does not by itself reopen board participation or true selection authority",
            },
            {
                "gap_name": "board_event_alignment",
                "current_status": "explicit_layer_now_present",
                "blocker_strength": "supporting_only",
                "evidence": f"aligned_board_supportive_count={board_alignment['summary']['aligned_board_supportive_count']}; lockout_misaligned_count={board_alignment['summary']['lockout_misaligned_count']}; raw_only_alignment_absent_count={board_alignment['summary']['raw_only_alignment_absent_count']}",
                "promotion_effect": "closes the intuition gap around event-board fit but still leaves true selection blocked when carrier and counterpanel evidence remain thin",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(gap_rows[0].keys()))
            writer.writeheader()
            writer.writerows(gap_rows)

        closed_gap_count = sum(
            1 for row in gap_rows if row["current_status"] == "explicit_layer_now_present"
        )
        remaining_hard_gap_count = sum(1 for row in gap_rows if row["blocker_strength"] == "hard")
        summary = {
            "acceptance_posture": "freeze_v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1",
            "named_gap_total": len(gap_rows),
            "explicitly_closed_gap_count": closed_gap_count,
            "remaining_hard_gap_count": remaining_hard_gap_count,
            "capital_true_selection_ready": False,
            "readiness_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "capital_true_selection remains blocked: the stack now has explicit followthrough and board-event alignment layers, but promotion is still denied until carrier evidence and anchor-decoy counterpanel thickness improve beyond single-case dependence",
        }
        interpretation = [
            "V1.34IM converts the named-gap stack into an explicit readiness audit instead of leaving the promotion block informal.",
            "The audit records partial progress honestly: two gaps are now explicit layers, but two hard evidence gaps still prevent any lawful true-selection upgrade.",
        ]
        return V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Report(
            summary=summary,
            gap_rows=gap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
