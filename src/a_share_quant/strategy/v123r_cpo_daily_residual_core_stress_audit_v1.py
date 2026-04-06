from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v123_daily_residual_downside_utils import build_research_daily_state_map


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123RCpoDailyResidualCoreStressAuditReport:
    summary: dict[str, Any]
    core_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "core_rows": self.core_rows,
            "interpretation": self.interpretation,
        }


class V123RCpoDailyResidualCoreStressAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v123m_payload: dict[str, Any]) -> V123RCpoDailyResidualCoreStressAuditReport:
        state_map = build_research_daily_state_map(repo_root=self.repo_root)
        interval_start = str(v123m_payload["summary"]["residual_interval_start"])
        interval_end = str(v123m_payload["summary"]["residual_interval_end"])
        score_field = str(v123m_payload["summary"]["selected_candidate_name"])
        positive_rows = [
            row
            for row in v123m_payload["scored_rows"]
            if bool(row["positive_label"]) and interval_start <= str(row["trade_date"]) <= interval_end
        ]

        running_peak = 0.0
        drawdown_rows: list[dict[str, Any]] = []
        for row in positive_rows:
            equity = _to_float(state_map[str(row["trade_date"])]["equity"])
            running_peak = max(running_peak, equity)
            drawdown_depth = 0.0 if running_peak <= 0 else 1.0 - equity / running_peak
            drawdown_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "score": _to_float(row[score_field]),
                    "drawdown_depth": round(drawdown_depth, 6),
                }
            )

        sorted_depths = sorted(row["drawdown_depth"] for row in drawdown_rows)
        median_depth = sorted_depths[len(sorted_depths) // 2]
        core_rows = []
        for row in drawdown_rows:
            core_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "drawdown_depth": row["drawdown_depth"],
                    "core_stress_label": row["drawdown_depth"] >= median_depth,
                    "held_pair_deterioration_score": round(row["score"], 6),
                }
            )

        core_positive = [row for row in core_rows if bool(row["core_stress_label"])]
        fringe_positive = [row for row in core_rows if not bool(row["core_stress_label"])]
        core_mean = sum(_to_float(row["held_pair_deterioration_score"]) for row in core_positive) / len(core_positive)
        fringe_mean = sum(_to_float(row["held_pair_deterioration_score"]) for row in fringe_positive) / len(fringe_positive)
        core_above_fringe_rate = (
            sum(
                1
                for row in core_positive
                if _to_float(row["held_pair_deterioration_score"]) >= fringe_mean
            )
            / len(core_positive)
        )
        summary = {
            "acceptance_posture": "freeze_v123r_cpo_daily_residual_core_stress_audit_v1",
            "candidate_name": score_field,
            "positive_interval_row_count": len(core_rows),
            "core_stress_row_count": len(core_positive),
            "fringe_row_count": len(fringe_positive),
            "core_drawdown_median_threshold": round(median_depth, 6),
            "core_mean_score": round(core_mean, 6),
            "fringe_mean_score": round(fringe_mean, 6),
            "core_minus_fringe_mean_score_gap": round(core_mean - fringe_mean, 6),
            "core_above_fringe_rate": round(core_above_fringe_rate, 6),
            "core_focus_posture": "core_focused" if core_mean > fringe_mean else "diffuse_inside_interval",
            "recommended_next_posture": "granular_boundary_audit_against_core_and_fringe",
        }
        interpretation = [
            "V1.23R asks whether the residual downside branch concentrates on the painful core of the third drawdown or just lights up the whole interval indiscriminately.",
            "The core label is defined by drawdown depth inside the positive interval, not by a new replay rule.",
            "A useful residual downside branch should score the deeper drawdown core higher than the fringe positive days.",
        ]
        return V123RCpoDailyResidualCoreStressAuditReport(
            summary=summary,
            core_rows=core_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123RCpoDailyResidualCoreStressAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    v123m_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    analyzer = V123RCpoDailyResidualCoreStressAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v123m_payload=v123m_payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123r_cpo_daily_residual_core_stress_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
