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
class V119LCpoParticipationTurnoverElgSupportDiscoveryReport:
    summary: dict[str, Any]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V119LCpoParticipationTurnoverElgSupportDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119LCpoParticipationTurnoverElgSupportDiscoveryReport:
        base_rows = json.loads(
            (self.repo_root / "reports" / "analysis" / "v119h_cpo_participation_turnover_combo_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        )["candidate_score_rows"]
        moneyflow_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv"
            )
        }

        raw_rows: list[dict[str, Any]] = []
        for row in base_rows:
            key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
            moneyflow = moneyflow_rows.get(key)
            if moneyflow is None:
                continue
            elg_ratio = (_to_float(moneyflow.get("buy_elg_amount")) + 1.0) / (
                _to_float(moneyflow.get("sell_elg_amount")) + 1.0
            )
            raw_rows.append(
                {
                    **row,
                    "elg_buy_sell_ratio": elg_ratio,
                }
            )

        elg_values = [_to_float(row["elg_buy_sell_ratio"]) for row in raw_rows]
        elg_mean = sum(elg_values) / len(elg_values)
        elg_std = math.sqrt(sum((value - elg_mean) ** 2 for value in elg_values) / len(elg_values)) or 1.0

        candidate_score_rows: list[dict[str, Any]] = []
        for row in raw_rows:
            score = _to_float(row["participation_turnover_combo_score"]) + 0.25 * _zscore(
                _to_float(row["elg_buy_sell_ratio"]), elg_mean, elg_std
            )
            candidate_score_rows.append(
                {
                    **row,
                    "participation_turnover_elg_support_score": round(score, 6),
                    "elg_buy_sell_ratio": round(_to_float(row["elg_buy_sell_ratio"]), 6),
                }
            )

        candidate_score_rows.sort(
            key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["participation_turnover_elg_support_score"]))
        )

        positive_rows = [row for row in candidate_score_rows if bool(row["positive_add_label"])]
        negative_rows = [row for row in candidate_score_rows if not bool(row["positive_add_label"])]
        positive_mean = sum(_to_float(row["participation_turnover_elg_support_score"]) for row in positive_rows) / len(
            positive_rows
        )
        negative_mean = sum(_to_float(row["participation_turnover_elg_support_score"]) for row in negative_rows) / len(
            negative_rows
        )

        summary = {
            "acceptance_posture": "freeze_v119l_cpo_participation_turnover_elg_support_discovery_v1",
            "candidate_discriminator_name": "participation_turnover_elg_support_score_candidate",
            "row_count": len(candidate_score_rows),
            "positive_add_row_count": len(positive_rows),
            "negative_add_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "combo_formula": "participation_turnover_combo_score + 0.25 * z(elg_buy_sell_ratio)",
            "recommended_next_posture": "externally_audit_elg_supported_combo_candidate_before_any_new_family_expansion",
        }
        interpretation = [
            "V1.19L adds exactly one new orthogonal support term to the live combo branch: extra-large-order buy-sell balance.",
            "The intent is narrow: test whether elite flow support repairs the 2024 holdout weakness without reopening a full feature-search loop.",
            "This remains non-replay and candidate-only until broader external and chronology checks agree.",
        ]
        return V119LCpoParticipationTurnoverElgSupportDiscoveryReport(
            summary=summary,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119LCpoParticipationTurnoverElgSupportDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119LCpoParticipationTurnoverElgSupportDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119l_cpo_participation_turnover_elg_support_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
