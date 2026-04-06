from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125n_commercial_aerospace_structural_regime_discovery_v1 import (
    V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer,
)


LOOKBACK = 30


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V125SCommercialAerospacePointInTimeRegimeProxyReport:
    summary: dict[str, Any]
    regime_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "regime_rows": self.regime_rows,
            "interpretation": self.interpretation,
        }


class V125SCommercialAerospacePointInTimeRegimeProxyAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _classify(self, current: dict[str, Any], history: list[dict[str, Any]]) -> str:
        if len(history) < LOOKBACK:
            return "warmup_neutral"

        ret_q75 = _quantile([float(row["control_avg_return"]) for row in history], 0.75)
        ret_q25 = _quantile([float(row["control_avg_return"]) for row in history], 0.25)
        breadth_q75 = _quantile([float(row["control_positive_breadth"]) for row in history], 0.75)
        breadth_q25 = _quantile([float(row["control_positive_breadth"]) for row in history], 0.25)
        conf_q75 = _quantile([float(row["confirmation_positive_breadth"]) for row in history], 0.75)
        cont_q75 = _quantile([float(row["continuation_support"]) for row in history], 0.75)
        heat_q75 = _quantile([float(row["control_limit_heat"]) for row in history], 0.75)
        sent_q75 = _quantile([float(row["sentiment_positive_breadth"]) for row in history], 0.75)
        risk_combo_q75 = _quantile(
            [float(row["turning_point_risk"]) + float(row["termination_risk"]) for row in history],
            0.75,
        )

        control_avg_return = float(current["control_avg_return"])
        control_positive_breadth = float(current["control_positive_breadth"])
        confirmation_positive_breadth = float(current["confirmation_positive_breadth"])
        continuation_support = float(current["continuation_support"])
        turning_point_risk = float(current["turning_point_risk"])
        termination_risk = float(current["termination_risk"])
        control_limit_heat = float(current["control_limit_heat"])
        sentiment_positive_breadth = float(current["sentiment_positive_breadth"])
        risk_combo = turning_point_risk + termination_risk

        strength = (
            control_avg_return >= ret_q75
            and control_positive_breadth >= breadth_q75
            and confirmation_positive_breadth >= conf_q75
        )
        continuation_backing = (
            continuation_support >= cont_q75
            and continuation_support > risk_combo
        )
        risk_off = (
            risk_combo >= risk_combo_q75
            and control_avg_return <= ret_q25
            and control_positive_breadth <= breadth_q25
        )
        overdrive = (
            control_limit_heat >= heat_q75
            and sentiment_positive_breadth >= sent_q75
            and not continuation_backing
        )

        if strength and continuation_backing:
            return "impulse_expansion_proxy"
        if risk_off:
            return "risk_off_deterioration_proxy"
        if overdrive:
            return "sentiment_overdrive_transition_proxy"
        return "weak_drift_chop_proxy"

    def analyze(self) -> V125SCommercialAerospacePointInTimeRegimeProxyReport:
        upstream = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(self.repo_root)
        date_rows = upstream._date_feature_rows()
        date_rows.sort(key=lambda row: row["trade_date"])

        regime_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(date_rows):
            history = date_rows[max(0, idx - LOOKBACK) : idx]
            regime_proxy_semantic = self._classify(row, history)
            regime_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "regime_proxy_semantic": regime_proxy_semantic,
                    "control_avg_return": round(float(row["control_avg_return"]), 8),
                    "control_positive_breadth": round(float(row["control_positive_breadth"]), 8),
                    "control_limit_heat": round(float(row["control_limit_heat"]), 8),
                    "confirmation_positive_breadth": round(float(row["confirmation_positive_breadth"]), 8),
                    "sentiment_positive_breadth": round(float(row["sentiment_positive_breadth"]), 8),
                    "continuation_support": round(float(row["continuation_support"]), 8),
                    "turning_point_risk": round(float(row["turning_point_risk"]), 8),
                    "termination_risk": round(float(row["termination_risk"]), 8),
                }
            )

        counts: dict[str, int] = {}
        for row in regime_rows:
            counts[row["regime_proxy_semantic"]] = counts.get(row["regime_proxy_semantic"], 0) + 1

        summary = {
            "acceptance_posture": "freeze_v125s_commercial_aerospace_point_in_time_regime_proxy_v1",
            "date_count": len(regime_rows),
            "lookback_days": LOOKBACK,
            "proxy_regime_counts": counts,
            "authoritative_rule": "commercial_aerospace_supervised_learning_must_use_point_in_time_regime_proxy_not_full_sample_cluster_semantic",
        }
        interpretation = [
            "V1.25S replaces full-sample regime backfill with a point-in-time regime proxy built from same-day board state and history-only thresholds.",
            "This proxy is lawful for EOD supervision because it does not require future clustering or retrospective segment relabeling.",
        ]
        return V125SCommercialAerospacePointInTimeRegimeProxyReport(
            summary=summary,
            regime_rows=regime_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125SCommercialAerospacePointInTimeRegimeProxyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_csv_file(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125SCommercialAerospacePointInTimeRegimeProxyAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125s_commercial_aerospace_point_in_time_regime_proxy_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_point_in_time_regime_proxy_v1.csv",
        rows=result.regime_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
