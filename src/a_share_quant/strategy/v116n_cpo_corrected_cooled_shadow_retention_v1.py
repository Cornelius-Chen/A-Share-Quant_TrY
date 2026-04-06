from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V116NCpoCorrectedCooledShadowRetentionReport:
    summary: dict[str, Any]
    retained_variant_row: dict[str, Any]
    hot_upper_bound_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_variant_row": self.retained_variant_row,
            "hot_upper_bound_row": self.hot_upper_bound_row,
            "interpretation": self.interpretation,
        }


class V116NCpoCorrectedCooledShadowRetentionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116k_payload: dict[str, Any],
        v116m_payload: dict[str, Any],
    ) -> V116NCpoCorrectedCooledShadowRetentionReport:
        variant_map = {str(row["variant_name"]): row for row in list(v116k_payload.get("variant_rows", []))}
        retained_name = str(v116m_payload.get("summary", {}).get("corrected_retained_shadow_variant"))
        hot_name = str(v116m_payload.get("summary", {}).get("hot_upper_bound_variant"))
        retained_row = dict(variant_map[retained_name])
        hot_row = dict(variant_map[hot_name])

        summary = {
            "acceptance_posture": "freeze_v116n_cpo_corrected_cooled_shadow_retention_v1",
            "candidate_posture": "cooled_shadow_only_not_promotable",
            "retained_variant_name": retained_name,
            "retained_final_equity": _to_float(retained_row.get("final_equity")),
            "retained_max_drawdown": _to_float(retained_row.get("max_drawdown")),
            "hot_upper_bound_variant_name": hot_name,
            "hot_upper_bound_final_equity": _to_float(hot_row.get("final_equity")),
            "hot_upper_bound_max_drawdown": _to_float(hot_row.get("max_drawdown")),
            "recommended_next_posture": "carry_corrected_cooled_shadow_candidate_forward_and_keep_hot_upper_bound_audit_only",
        }
        interpretation = [
            "V1.16N corrects the retention mistake in V116L after the formal three-run adversarial review over V116J/V116K/V116L.",
            "The retained object is now the cleanest cooled-shadow candidate rather than the highest-equity hottest replay line.",
            "This corrected retained object remains candidate-only and must not be promoted into law without broader repaired-window revalidation.",
        ]
        return V116NCpoCorrectedCooledShadowRetentionReport(
            summary=summary,
            retained_variant_row=retained_row,
            hot_upper_bound_row=hot_row,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116NCpoCorrectedCooledShadowRetentionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116NCpoCorrectedCooledShadowRetentionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116k_payload=json.loads((repo_root / "reports" / "analysis" / "v116k_cpo_visible_only_shadow_heat_trim_review_v1.json").read_text(encoding="utf-8")),
        v116m_payload=json.loads((repo_root / "reports" / "analysis" / "v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116n_cpo_corrected_cooled_shadow_retention_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
