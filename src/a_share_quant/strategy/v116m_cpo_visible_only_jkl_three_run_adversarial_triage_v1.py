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
class V116MCpoVisibleOnlyJklThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V116MCpoVisibleOnlyJklThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116j_payload: dict[str, Any],
        v116k_payload: dict[str, Any],
        v116l_payload: dict[str, Any],
    ) -> V116MCpoVisibleOnlyJklThreeRunAdversarialTriageReport:
        _ = v116j_payload
        variant_map = {str(row["variant_name"]): row for row in list(v116k_payload.get("variant_rows", []))}
        earliest_row = dict(variant_map["earliest_visible_reference"])
        corrected_row = dict(variant_map["double_confirm_late_quarter"])
        v116l_summary = dict(v116l_payload.get("summary", {}))
        v116l_row = dict(v116l_payload.get("retained_variant_row", {}))

        triage_rows = [
            {
                "triage_target": "earliest_visible_reference",
                "triage_posture": "demote_to_hot_upper_bound_only",
                "reason": "v116l_reselected_hottest_line_instead_of_cooled_candidate",
                "final_equity": _to_float(earliest_row.get("final_equity")),
                "max_drawdown": _to_float(earliest_row.get("max_drawdown")),
                "executed_order_count": int(earliest_row.get("executed_order_count", 0)),
            },
            {
                "triage_target": "double_confirm_late_quarter",
                "triage_posture": "retain_as_corrected_cooled_shadow_candidate",
                "reason": "lowest_heat_among_executing_double_confirm_variants",
                "final_equity": _to_float(corrected_row.get("final_equity")),
                "max_drawdown": _to_float(corrected_row.get("max_drawdown")),
                "executed_order_count": int(corrected_row.get("executed_order_count", 0)),
            },
            {
                "triage_target": "v116l_retention_result",
                "triage_posture": "overruled",
                "reason": "retention_scoring_overweighted_equity",
                "retained_variant_name": str(v116l_summary.get("retained_variant_name")),
                "retained_final_equity": _to_float(v116l_row.get("final_equity")),
                "retained_max_drawdown": _to_float(v116l_row.get("max_drawdown")),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1",
            "review_scope": "v116j_v116k_v116l",
            "hot_upper_bound_variant": "earliest_visible_reference",
            "corrected_retained_shadow_variant": "double_confirm_late_quarter",
            "v116l_retention_valid": False,
            "recommended_next_posture": "replace_v116l_retention_with_corrected_cooled_shadow_retention_and_continue_candidate_only",
        }
        interpretation = [
            "The second three-run adversarial review over V116J/V116K/V116L concludes that the wider visible-only line still contains signal, but the hottest replay line cannot be kept as the cooled retained object.",
            "V116L is overruled because it retained `earliest_visible_reference`, which conflicts with the explicit heat-trim intent of V116K.",
            "The only corrected cooled-shadow retained candidate after triage is `double_confirm_late_quarter`; `earliest_visible_reference` remains an audit-only hot upper bound.",
        ]
        return V116MCpoVisibleOnlyJklThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116MCpoVisibleOnlyJklThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116MCpoVisibleOnlyJklThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
        v116k_payload=json.loads((repo_root / "reports" / "analysis" / "v116k_cpo_visible_only_shadow_heat_trim_review_v1.json").read_text(encoding="utf-8")),
        v116l_payload=json.loads((repo_root / "reports" / "analysis" / "v116l_cpo_visible_only_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
