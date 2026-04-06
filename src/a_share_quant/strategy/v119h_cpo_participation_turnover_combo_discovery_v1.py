from __future__ import annotations

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


def _zscore(value: float, mean_value: float, std_value: float) -> float:
    if std_value == 0.0:
        return 0.0
    return (value - mean_value) / std_value


@dataclass(slots=True)
class V119HCpoParticipationTurnoverComboDiscoveryReport:
    summary: dict[str, Any]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V119HCpoParticipationTurnoverComboDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v118t_payload: dict[str, Any],
        v119d_payload: dict[str, Any],
    ) -> V119HCpoParticipationTurnoverComboDiscoveryReport:
        participation_rows = {
            (str(row["signal_trade_date"]), str(row["symbol"])): row
            for row in v118t_payload.get("candidate_score_rows", [])
        }
        turnover_rows = {
            (str(row["signal_trade_date"]), str(row["symbol"])): row
            for row in v119d_payload.get("candidate_score_rows", [])
        }
        keys = sorted(set(participation_rows.keys()) & set(turnover_rows.keys()))
        joined_rows: list[dict[str, Any]] = []
        participation_scores = [
            _to_float(participation_rows[key]["sustained_participation_non_chase_score"])
            for key in keys
        ]
        turnover_scores = [
            _to_float(turnover_rows[key]["turnover_discipline_score_candidate"])
            for key in keys
        ]
        participation_mean = sum(participation_scores) / len(participation_scores)
        turnover_mean = sum(turnover_scores) / len(turnover_scores)
        participation_std = math.sqrt(
            sum((value - participation_mean) ** 2 for value in participation_scores) / len(participation_scores)
        ) or 1.0
        turnover_std = math.sqrt(
            sum((value - turnover_mean) ** 2 for value in turnover_scores) / len(turnover_scores)
        ) or 1.0

        for key in keys:
            participation_row = participation_rows[key]
            turnover_row = turnover_rows[key]
            participation_z = _zscore(
                _to_float(participation_row["sustained_participation_non_chase_score"]),
                participation_mean,
                participation_std,
            )
            turnover_z = _zscore(
                _to_float(turnover_row["turnover_discipline_score_candidate"]),
                turnover_mean,
                turnover_std,
            )
            combo_score = participation_z + turnover_z
            joined_rows.append(
                {
                    "signal_trade_date": key[0],
                    "symbol": key[1],
                    "positive_add_label": bool(turnover_row["positive_add_label"]),
                    "expectancy_proxy_3d": _to_float(turnover_row["expectancy_proxy_3d"]),
                    "max_adverse_return_3d": _to_float(turnover_row["max_adverse_return_3d"]),
                    "sustained_participation_non_chase_score": _to_float(
                        participation_row["sustained_participation_non_chase_score"]
                    ),
                    "turnover_discipline_score_candidate": _to_float(
                        turnover_row["turnover_discipline_score_candidate"]
                    ),
                    "participation_turnover_combo_score": round(combo_score, 6),
                }
            )
        joined_rows.sort(
            key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["participation_turnover_combo_score"]))
        )

        positive_rows = [row for row in joined_rows if bool(row["positive_add_label"])]
        negative_rows = [row for row in joined_rows if not bool(row["positive_add_label"])]
        positive_mean = sum(_to_float(row["participation_turnover_combo_score"]) for row in positive_rows) / len(positive_rows)
        negative_mean = sum(_to_float(row["participation_turnover_combo_score"]) for row in negative_rows) / len(negative_rows)

        summary = {
            "acceptance_posture": "freeze_v119h_cpo_participation_turnover_combo_discovery_v1",
            "candidate_discriminator_name": "participation_turnover_combo_score_candidate",
            "row_count": len(joined_rows),
            "positive_add_row_count": len(positive_rows),
            "negative_add_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "combo_formula": "z(participation_non_chase) + z(turnover_discipline)",
            "recommended_next_posture": "externally_audit_combo_candidate_and_check_if_2024_holdout_hole_shrinks",
        }
        interpretation = [
            "V1.19H opens a minimal orthogonal combo branch by combining the strongest live intraday participation line with the new Tushare turnover-discipline line.",
            "The intent is not to stack everything, only to see whether one clean participation signal plus one clean daily-float/turnover signal repairs the remaining 2024 chronology hole.",
            "This remains non-replay and candidate-only until broader audit and time-split checks agree.",
        ]
        return V119HCpoParticipationTurnoverComboDiscoveryReport(
            summary=summary,
            candidate_score_rows=joined_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119HCpoParticipationTurnoverComboDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119HCpoParticipationTurnoverComboDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118t_payload=json.loads((repo_root / "reports" / "analysis" / "v118t_cpo_sustained_participation_non_chase_discovery_v1.json").read_text(encoding="utf-8")),
        v119d_payload=json.loads((repo_root / "reports" / "analysis" / "v119d_cpo_tushare_turnover_discipline_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119h_cpo_participation_turnover_combo_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
