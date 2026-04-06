from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.frontier_path = analysis_dir / "v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1.json"
        self.inventory_path = analysis_dir / "v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1.json"
        self.applicability_path = analysis_dir / "v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1.json"
        self.symbol_pool_gap_path = analysis_dir / "v134jq_commercial_aerospace_broader_symbol_pool_materialization_gap_audit_v1.json"
        self.heat_axis_path = analysis_dir / "v134js_commercial_aerospace_heat_axis_counterpanel_expansion_audit_v1.json"
        self.carrier_follow_path = analysis_dir / "v134ju_commercial_aerospace_carrier_follow_search_expansion_audit_v1.json"
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_broader_attention_frontier_status_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze(self) -> V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Report:
        frontier = self._load_json(self.frontier_path)
        inventory = self._load_json(self.inventory_path)
        applicability = self._load_json(self.applicability_path)
        symbol_pool_gap = self._load_json(self.symbol_pool_gap_path)
        heat_axis = self._load_json(self.heat_axis_path)
        carrier_follow = self._load_json(self.carrier_follow_path)

        status_rows = [
            {
                "branch": "broader_symbol_pool_expander",
                "branch_state": "formalized_same_plane_branch",
                "progress_type": "source_ready_but_not_materialized",
                "operative_blocker": "name_to_symbol_coverage_gap",
                "promotion_state": "blocked",
                "detail": f"materialized_symbol_count = {symbol_pool_gap['summary']['materialized_symbol_count']}",
            },
            {
                "branch": "heat_axis_and_counterpanel_expander",
                "branch_state": "formalized_same_plane_branch",
                "progress_type": "singleton_reinforcement_only",
                "operative_blocker": "counterpanel_not_thickened",
                "promotion_state": "blocked",
                "detail": (
                    "same_plane_counterpanel_expansion_ready_count = "
                    f"{heat_axis['summary']['same_plane_counterpanel_expansion_ready_count']}"
                ),
            },
            {
                "branch": "carrier_follow_search_expander",
                "branch_state": "formalized_same_plane_branch",
                "progress_type": "known_case_reinforcement_only",
                "operative_blocker": "branch_not_promotive",
                "promotion_state": "blocked",
                "detail": f"linked_local_case_count = {carrier_follow['summary']['linked_local_case_count']}",
            },
            {
                "branch": "capital_true_selection",
                "branch_state": "downstream_consumer",
                "progress_type": "not_open",
                "operative_blocker": "all_three_live_branches_stop_before_promotion",
                "promotion_state": "blocked",
                "detail": "same-plane branches exist but none crosses into promotive evidence",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134jw_commercial_aerospace_broader_attention_frontier_status_audit_v1",
            "frontier_state": frontier["summary"]["frontier_state"],
            "ready_local_broader_source_count": inventory["summary"]["ready_local_broader_source_count"],
            "same_plane_ready_source_count": applicability["summary"]["same_plane_ready_source_count"],
            "formalized_same_plane_branch_count": 3,
            "promotive_branch_count": 0,
            "blocked_consumer_count": 1,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_attention_frontier_status_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JW consolidates the broader-attention-evidence frontier after all three same-plane branches have been formally opened.",
            "The frontier is real, but every live branch still stops short of promotion for a different explicit reason: materialization gap, counterpanel thinness, or reinforcement-only evidence.",
        ]
        return V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jw_commercial_aerospace_broader_attention_frontier_status_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
