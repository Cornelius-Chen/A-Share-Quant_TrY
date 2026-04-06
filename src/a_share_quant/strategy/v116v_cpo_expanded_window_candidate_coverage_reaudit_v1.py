from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1 import (
    V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer,
)


@dataclass(slots=True)
class V116VCpoExpandedWindowCandidateCoverageReauditReport:
    summary: dict[str, Any]
    coverage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "coverage_rows": self.coverage_rows,
            "interpretation": self.interpretation,
        }


class V116VCpoExpandedWindowCandidateCoverageReauditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v116q_payload: dict[str, Any],
        merged_pca_rows_path: Path,
    ) -> V116VCpoExpandedWindowCandidateCoverageReauditReport:
        base = V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer(repo_root=self.repo_root).analyze(
            v114t_payload=v114t_payload,
            v116q_payload=v116q_payload,
            pca_rows_path=merged_pca_rows_path,
        )
        true_gap_rows = [row for row in base.coverage_rows if bool(row.get("coverage_gap"))]
        summary = {
            "acceptance_posture": "freeze_v116v_cpo_expanded_window_candidate_coverage_reaudit_v1",
            "expanded_window_day_count": int(base.summary.get("expanded_window_day_count", 0)),
            "days_with_add_candidate_rows": int(base.summary.get("days_with_add_candidate_rows", 0)),
            "days_with_held_mature_symbols": int(base.summary.get("days_with_held_mature_symbols", 0)),
            "true_coverage_gap_day_count_after_rebuild": len(true_gap_rows),
            "recommended_next_posture": "rerun_corrected_cooled_shadow_expanded_window_validation_on_rebuilt_candidate_base_if_true_gap_days_are_cleared",
        }
        interpretation = [
            "V1.16V reruns the V116S-style coverage audit on the merged PCA band table after the expanded-window action-timepoint rebuild.",
            "The purpose is not to judge signal quality yet, but to verify whether the true held-mature coverage gaps on 2023-11-07, 2024-01-18, and 2024-01-23 have actually been repaired.",
            "Only after the coverage layer is repaired does it make sense to re-run visible-only candidate validation on the expanded window.",
        ]
        return V116VCpoExpandedWindowCandidateCoverageReauditReport(
            summary=summary,
            coverage_rows=base.coverage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116VCpoExpandedWindowCandidateCoverageReauditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116VCpoExpandedWindowCandidateCoverageReauditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        merged_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116v_cpo_expanded_window_candidate_coverage_reaudit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
