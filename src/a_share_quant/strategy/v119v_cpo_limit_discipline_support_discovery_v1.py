from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _zscore(value: float, mean_value: float, std_value: float) -> float:
    if std_value == 0.0:
        return 0.0
    return (value - mean_value) / std_value


@dataclass(slots=True)
class V119VCpoLimitDisciplineSupportDiscoveryReport:
    summary: dict[str, Any]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V119VCpoLimitDisciplineSupportDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119VCpoLimitDisciplineSupportDiscoveryReport:
        parent_payload = json.loads(
            (
                self.repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json"
            ).read_text(encoding="utf-8")
        )
        parent_rows = parent_payload["candidate_score_rows"]
        daily_bar_rows = {
            (str(row["trade_date"]).replace("-", ""), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
            )
        }
        stk_limit_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "reference" / "stk_limit" / "tushare_cpo_stk_limit_v1.csv"
            )
        }

        raw_rows: list[dict[str, Any]] = []
        for row in parent_rows:
            trade_date = str(row["signal_trade_date"]).replace("-", "")
            key = (trade_date, str(row["symbol"]))
            daily_bar = daily_bar_rows.get(key)
            stk_limit = stk_limit_rows.get(key)
            if daily_bar is None or stk_limit is None:
                continue
            pre_close = _to_float(daily_bar["pre_close"])
            close = _to_float(daily_bar["close"])
            high = _to_float(daily_bar["high"])
            up_limit = _to_float(stk_limit["up_limit"])
            if up_limit <= pre_close:
                continue
            up_gap = (up_limit - close) / max(abs(up_limit), 1e-9)
            close_to_up_band = (close - pre_close) / max(up_limit - pre_close, 1e-9)
            high_to_up_band = (high - pre_close) / max(up_limit - pre_close, 1e-9)
            raw_rows.append(
                {
                    **row,
                    "up_gap": up_gap,
                    "close_to_up_band": close_to_up_band,
                    "high_to_up_band": high_to_up_band,
                }
            )

        up_gap_values = [_to_float(row["up_gap"]) for row in raw_rows]
        close_to_up_values = [_to_float(row["close_to_up_band"]) for row in raw_rows]
        high_to_up_values = [_to_float(row["high_to_up_band"]) for row in raw_rows]
        up_gap_mean = sum(up_gap_values) / len(up_gap_values)
        close_to_up_mean = sum(close_to_up_values) / len(close_to_up_values)
        high_to_up_mean = sum(high_to_up_values) / len(high_to_up_values)
        up_gap_std = math.sqrt(sum((value - up_gap_mean) ** 2 for value in up_gap_values) / len(up_gap_values)) or 1.0
        close_to_up_std = math.sqrt(
            sum((value - close_to_up_mean) ** 2 for value in close_to_up_values) / len(close_to_up_values)
        ) or 1.0
        high_to_up_std = math.sqrt(
            sum((value - high_to_up_mean) ** 2 for value in high_to_up_values) / len(high_to_up_values)
        ) or 1.0

        candidate_score_rows: list[dict[str, Any]] = []
        for row in raw_rows:
            score = (
                _to_float(row["participation_turnover_elg_support_score"])
                + 0.05 * _zscore(_to_float(row["up_gap"]), up_gap_mean, up_gap_std)
                - 0.05 * _zscore(_to_float(row["close_to_up_band"]), close_to_up_mean, close_to_up_std)
                - 0.05 * _zscore(_to_float(row["high_to_up_band"]), high_to_up_mean, high_to_up_std)
            )
            candidate_score_rows.append(
                {
                    **row,
                    "limit_discipline_support_score": round(score, 6),
                }
            )

        candidate_score_rows.sort(
            key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["limit_discipline_support_score"]))
        )
        positive_rows = [row for row in candidate_score_rows if bool(row["positive_add_label"])]
        negative_rows = [row for row in candidate_score_rows if not bool(row["positive_add_label"])]
        positive_mean = sum(_to_float(row["limit_discipline_support_score"]) for row in positive_rows) / len(positive_rows)
        negative_mean = sum(_to_float(row["limit_discipline_support_score"]) for row in negative_rows) / len(negative_rows)
        summary = {
            "acceptance_posture": "freeze_v119v_cpo_limit_discipline_support_discovery_v1",
            "candidate_discriminator_name": "limit_discipline_support_score_candidate",
            "row_count": len(candidate_score_rows),
            "positive_add_row_count": len(positive_rows),
            "negative_add_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "parent_score_mean_gap_positive_minus_negative": parent_payload["summary"][
                "candidate_score_mean_gap_positive_minus_negative"
            ],
            "increment_posture_vs_parent": (
                "orthogonal_increment_found"
                if positive_mean - negative_mean > _to_float(parent_payload["summary"]["candidate_score_mean_gap_positive_minus_negative"])
                else "no_clear_increment_over_parent"
            ),
            "combo_formula": "participation_turnover_elg_support_score + 0.05*z(up_gap) - 0.05*z(close_to_up_band) - 0.05*z(high_to_up_band)",
            "recommended_next_posture": "externally_audit_limit_discipline_support_branch_once_then_kill_or_keep_quickly",
        }
        interpretation = [
            "V1.19V opens one narrow orthogonal repair idea: daily limit-band discipline, not another same-family residual tweak.",
            "The hypothesis is simple: positive add should prefer non-crowded extension and some distance from the pure up-limit chase posture.",
            "This branch is intentionally narrow and should be killed quickly if external or chronology checks show no real increment over the parent ELG-supported line.",
        ]
        return V119VCpoLimitDisciplineSupportDiscoveryReport(
            summary=summary,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119VCpoLimitDisciplineSupportDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119VCpoLimitDisciplineSupportDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119v_cpo_limit_discipline_support_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
