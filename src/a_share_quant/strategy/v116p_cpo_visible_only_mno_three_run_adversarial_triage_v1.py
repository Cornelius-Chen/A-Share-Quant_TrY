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
class V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116m_payload: dict[str, Any],
        v116n_payload: dict[str, Any],
        v116o_payload: dict[str, Any],
    ) -> V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageReport:
        _ = v116m_payload
        retained_name = str(v116n_payload.get("summary", {}).get("retained_variant_name"))
        variant_map = {str(row["variant_name"]): row for row in list(v116o_payload.get("variant_rows", []))}
        cooled_row = dict(variant_map["corrected_cooled_shadow_candidate"])
        hot_row = dict(variant_map["hot_upper_bound_reference"])

        triage_rows = [
            {
                "triage_target": retained_name,
                "triage_posture": "retain_candidate_only",
                "reason": "cleaner_than_hot_upper_bound_but_wider_revalidation_still_too_thin",
                "hit_day_count": int(cooled_row.get("hit_day_count", 0)),
                "hit_day_rate": _to_float(cooled_row.get("hit_day_rate")),
                "positive_expectancy_hit_rate": _to_float(cooled_row.get("positive_expectancy_hit_rate")),
                "avg_expectancy_proxy_3d": _to_float(cooled_row.get("avg_expectancy_proxy_3d")),
            },
            {
                "triage_target": "hot_upper_bound_reference",
                "triage_posture": "audit_only_upper_bound",
                "reason": "broader_coverage_but_too_mixed_and_too_hot",
                "hit_day_count": int(hot_row.get("hit_day_count", 0)),
                "hit_day_rate": _to_float(hot_row.get("hit_day_rate")),
                "positive_expectancy_hit_rate": _to_float(hot_row.get("positive_expectancy_hit_rate")),
                "avg_expectancy_proxy_3d": _to_float(hot_row.get("avg_expectancy_proxy_3d")),
            },
            {
                "triage_target": "next_step",
                "triage_posture": "expand_repaired_window_before_more_replay",
                "reason": "same_family_and_small_sample_risk_remains_primary_issue",
                "current_wider_window_day_count": int(v116o_payload.get("summary", {}).get("wider_window_day_count", 0)),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116p_cpo_visible_only_mno_three_run_adversarial_triage_v1",
            "review_scope": "v116m_v116n_v116o",
            "retained_candidate_still_valid": True,
            "promotion_allowed": False,
            "recommended_next_posture": "expand_repaired_window_sample_before_any_new_replay_facing_visible_only_expansion",
        }
        interpretation = [
            "The V116M/V116N/V116O triage accepts the corrected cooled-shadow retention but refuses to treat the wider revalidation as sufficient replay-facing evidence.",
            "The retained object stays alive only as a candidate-only shadow candidate; the hot upper bound remains useful only as a reference ceiling.",
            "The primary blocker is no longer retention coherence but repaired-window sample thinness and same-family overfitting risk.",
        ]
        return V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116m_payload=json.loads((repo_root / "reports" / "analysis" / "v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8")),
        v116n_payload=json.loads((repo_root / "reports" / "analysis" / "v116n_cpo_corrected_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
        v116o_payload=json.loads((repo_root / "reports" / "analysis" / "v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116p_cpo_visible_only_mno_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
