from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129PCommercialAerospaceNOPTransferPreparationTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129PCommercialAerospaceNOPTransferPreparationTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.selection_path = repo_root / "reports" / "analysis" / "v129n_commercial_aerospace_transfer_target_selection_v1.json"
        self.boundary_path = repo_root / "reports" / "analysis" / "v129o_commercial_aerospace_bk0480_portability_boundary_memo_v1.json"
        self.governance_triage_path = repo_root / "reports" / "analysis" / "v129m_commercial_aerospace_klm_governance_packaging_triage_v1.json"

    def analyze(self) -> V129PCommercialAerospaceNOPTransferPreparationTriageReport:
        selection = json.loads(self.selection_path.read_text(encoding="utf-8"))
        boundary = json.loads(self.boundary_path.read_text(encoding="utf-8"))
        governance_triage = json.loads(self.governance_triage_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "bk0480_transfer_preparation",
                "status": "start_as_next_primary_worker",
                "reason": "BK0480 is the closest adjacent aerospace board and best first portability test without archetype mixing.",
            },
            {
                "direction": "bk0808_transfer",
                "status": "keep_shadow_only",
                "reason": "BK0808 remains broader and noisier, so it should stay queued as a later shadow transfer target.",
            },
            {
                "direction": "portable_grammar",
                "status": "carry_forward",
                "reason": "Methodology, execution grammar compaction, downside-first repair sequence, and promotion discipline are portable.",
            },
            {
                "direction": "commercial_aerospace_local_semantics",
                "status": "hard_reset_before_bk0480_replay",
                "reason": "Chronology windows, symbol pressure maps, named rules, and board-specific archetype semantics must be relearned locally.",
            },
            {
                "direction": "commercial_aerospace_board_local_tuning",
                "status": "stop",
                "reason": governance_triage["summary"]["authoritative_rule"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129p_commercial_aerospace_nop_transfer_preparation_triage_v1",
            "recommended_next_primary_board": selection["summary"]["recommended_primary_transfer_target"],
            "recommended_next_primary_board_name": selection["summary"]["recommended_primary_transfer_board_name"],
            "shadow_later_board": selection["summary"]["shadow_later_target"],
            "portable_layer_count": boundary["summary"]["portable_layer_count"],
            "local_reset_layer_count": boundary["summary"]["local_reset_layer_count"],
            "authoritative_status": "start_bk0480_transfer_preparation_with_local_reset_and_keep_bk0808_as_shadow_only",
            "authoritative_rule": "transfer_the_grammar_and_governance_schema_but_not_the_commercial_aerospace_local_windows_symbol_facts_or_rule_names",
        }
        interpretation = [
            "V1.29P freezes the first post-commercial-aerospace move: BK0480 transfer preparation with explicit local reset.",
            "This keeps the proven methodology while preventing silent cloning of commercial-aerospace-specific chronology and symbol facts.",
        ]
        return V129PCommercialAerospaceNOPTransferPreparationTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129PCommercialAerospaceNOPTransferPreparationTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129PCommercialAerospaceNOPTransferPreparationTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129p_commercial_aerospace_nop_transfer_preparation_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
