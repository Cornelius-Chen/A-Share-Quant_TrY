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
class V116FCpoVisibleOnlyThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V116FCpoVisibleOnlyThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116c_payload: dict[str, Any],
        v116d_payload: dict[str, Any],
        v116e_payload: dict[str, Any],
    ) -> V116FCpoVisibleOnlyThreeRunAdversarialTriageReport:
        c_rows = {str(row["variant_name"]): row for row in v116c_payload.get("variant_rows", [])}
        d_rows = {str(row["variant_name"]): row for row in v116d_payload.get("variant_rows", [])}
        e_rows = {str(row["variant_name"]): row for row in v116e_payload.get("audit_rows", [])}

        retained_rows = [
            {
                "variant_name": "all_intraday_strict_visible",
                "retention_posture": "audit_ceiling_only",
                "reason": "visible-only rebuild direction is valid, but the all-pass ceiling remains too loose for promotion",
                "final_equity": _to_float(c_rows["all_intraday_strict_visible"]["final_equity"]),
                "max_drawdown": _to_float(c_rows["all_intraday_strict_visible"]["max_drawdown"]),
            },
            {
                "variant_name": "pc2_only_q_0p25",
                "retention_posture": "clean_coherent_candidate",
                "reason": "best current balance between visible-only execution, positive audit coherence, and moderate drawdown",
                "final_equity": _to_float(d_rows["pc2_only_q_0p25"]["final_equity"]),
                "max_drawdown": _to_float(d_rows["pc2_only_q_0p25"]["max_drawdown"]),
                "positive_expectancy_hit_rate": _to_float(e_rows["pc2_only_q_0p25"]["positive_expectancy_hit_rate"]),
            },
            {
                "variant_name": "pc1_or_pc2_q_0p25",
                "retention_posture": "expressive_shadow_candidate",
                "reason": "most expressive visible-only middle candidate, worth carrying as a shadow posture but not promoting",
                "final_equity": _to_float(d_rows["pc1_or_pc2_q_0p25"]["final_equity"]),
                "max_drawdown": _to_float(d_rows["pc1_or_pc2_q_0p25"]["max_drawdown"]),
                "positive_expectancy_hit_rate": _to_float(e_rows["pc1_or_pc2_q_0p25"]["positive_expectancy_hit_rate"]),
            },
        ]

        blocked_rows = [
            {
                "variant_name": "pc1_only_q_0p2",
                "block_reason": "audit_and_replay_direction_diverge",
                "final_equity": _to_float(d_rows["pc1_only_q_0p2"]["final_equity"]),
                "max_drawdown": _to_float(d_rows["pc1_only_q_0p2"]["max_drawdown"]),
                "positive_expectancy_hit_rate": _to_float(e_rows["pc1_only_q_0p2"]["positive_expectancy_hit_rate"]),
                "avg_expectancy_proxy_3d": _to_float(e_rows["pc1_only_q_0p2"]["avg_expectancy_proxy_3d"]),
            },
            {
                "variant_name": "all_intraday_strict_visible",
                "block_reason": "too_loose_for_promotion",
                "final_equity": _to_float(c_rows["all_intraday_strict_visible"]["final_equity"]),
                "max_drawdown": _to_float(c_rows["all_intraday_strict_visible"]["max_drawdown"]),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116f_cpo_visible_only_three_run_adversarial_triage_v1",
            "triage_window": ["V116C", "V116D", "V116E"],
            "retained_count": len(retained_rows),
            "blocked_count": len(blocked_rows),
            "must_fix_next": "time_split_threshold_rebuild_and_strict_checkpoint_to_fill_alignment",
            "recommended_next_posture": "carry_pc2_only_q_0p25_and_pc1_or_pc2_q_0p25_forward_as_candidate_only_after_time_split_rebuild",
        }
        interpretation = [
            "The first visible-only three-run adversarial review keeps the no-future-label rebuild but rejects immediate promotion of every executing variant.",
            "pc1_only_q_0p2 is no longer treated as the main clean candidate because audit coherence turns negative after the V116E alignment repair.",
            "The next mandatory repair is no longer filter tweaking inside the same sample, but time-split threshold rebuilding plus stricter checkpoint-to-fill semantics.",
        ]
        return V116FCpoVisibleOnlyThreeRunAdversarialTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116FCpoVisibleOnlyThreeRunAdversarialTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116FCpoVisibleOnlyThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116c_payload=json.loads((repo_root / "reports" / "analysis" / "v116c_cpo_visible_only_intraday_filter_rebuild_v1.json").read_text(encoding="utf-8")),
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        v116e_payload=json.loads((repo_root / "reports" / "analysis" / "v116e_cpo_visible_only_candidate_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116f_cpo_visible_only_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
