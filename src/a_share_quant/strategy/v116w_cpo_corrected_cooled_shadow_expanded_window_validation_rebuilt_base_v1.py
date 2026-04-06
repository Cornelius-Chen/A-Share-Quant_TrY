from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v116r_cpo_corrected_cooled_shadow_expanded_window_validation_v1 import (
    V116RCpoCorrectedCooledShadowExpandedWindowValidationAnalyzer,
)


@dataclass(slots=True)
class V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    hit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "hit_rows": self.hit_rows,
            "interpretation": self.interpretation,
        }


class V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116d_payload: dict[str, Any],
        v116q_payload: dict[str, Any],
        rebuilt_pca_rows_path: Path,
        training_view_path: Path,
        feature_base_path: Path,
    ) -> V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseReport:
        base = V116RCpoCorrectedCooledShadowExpandedWindowValidationAnalyzer(repo_root=self.repo_root).analyze(
            v116d_payload=v116d_payload,
            v116q_payload=v116q_payload,
            pca_rows_path=rebuilt_pca_rows_path,
            training_view_path=training_view_path,
            feature_base_path=feature_base_path,
        )
        summary = dict(base.summary)
        summary["acceptance_posture"] = "freeze_v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1"
        summary["candidate_base_source"] = "rebuilt_expanded_window_pca_band_rows"
        summary["recommended_next_posture"] = "judge_whether_new_day_hits_appear_now_that_candidate_base_coverage_is_repaired"
        interpretation = [
            "V1.16W reruns the V1.16R-style expanded-window validation after the candidate-base coverage repair in V116U/V116V.",
            "The visible-only filter family still uses only point-in-time-visible checkpoint scores; rebuilt rows are allowed into the base table, but future labels remain audit-only.",
            "This is the first clean read on whether the corrected cooled candidate failed because of missing rows or because the signal truly does not extend to the new expanded-window days.",
        ]
        return V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseReport(
            summary=summary,
            variant_rows=base.variant_rows,
            hit_rows=base.hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        rebuilt_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
