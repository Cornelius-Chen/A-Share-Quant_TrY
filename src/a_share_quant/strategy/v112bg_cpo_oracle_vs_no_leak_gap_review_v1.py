from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BGCPOOracleVsNoLeakGapReviewReport:
    summary: dict[str, Any]
    stage_gap_rows: list[dict[str, Any]]
    role_gap_rows: list[dict[str, Any]]
    catalyst_gap_rows: list[dict[str, Any]]
    margin_quality_rows: list[dict[str, Any]]
    recommendation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stage_gap_rows": self.stage_gap_rows,
            "role_gap_rows": self.role_gap_rows,
            "catalyst_gap_rows": self.catalyst_gap_rows,
            "margin_quality_rows": self.margin_quality_rows,
            "recommendation_rows": self.recommendation_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BGCPOOracleVsNoLeakGapReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        v112bc_protocol_payload: dict[str, Any],
    ) -> V112BGCPOOracleVsNoLeakGapReviewReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bg_now")):
            raise ValueError("V1.12BG must be open before the gap review runs.")
        if int(dict(v112bc_protocol_payload.get("summary", {})).get("no_leak_track_count", 0)) != 2:
            raise ValueError("V1.12BG requires the frozen no-leak portfolio protocol from V1.12BC.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        oracle_trades = list(oracle_benchmark_payload.get("trade_rows", []))
        aggressive_trades = list(aggressive_pilot_payload.get("trade_rows", []))
        if not oracle_trades or not aggressive_trades:
            raise ValueError("V1.12BG requires both oracle and aggressive trade traces.")

        stage_gap_rows = self._dimension_gap_rows(oracle_trades=oracle_trades, aggressive_trades=aggressive_trades, field_name="stage_family")
        role_gap_rows = self._dimension_gap_rows(oracle_trades=oracle_trades, aggressive_trades=aggressive_trades, field_name="role_family")
        catalyst_gap_rows = self._dimension_gap_rows(
            oracle_trades=oracle_trades,
            aggressive_trades=aggressive_trades,
            field_name="catalyst_sequence_label",
        )

        winner_margins: list[float] = []
        loser_margins: list[float] = []
        for row in aggressive_trades:
            realized = float(row.get("realized_forward_return_20d", 0.0))
            margin = float(row.get("predicted_winner_prob", 0.0)) - float(row.get("training_base_rate", 0.0))
            if realized > 0.0:
                winner_margins.append(margin)
            elif realized < 0.0:
                loser_margins.append(margin)

        winner_margin_mean = sum(winner_margins) / len(winner_margins) if winner_margins else 0.0
        loser_margin_mean = sum(loser_margins) / len(loser_margins) if loser_margins else 0.0
        recommended_margin_floor = round(max(0.08, (winner_margin_mean + loser_margin_mean) / 2.0), 4)

        negative_stage = max(
            ((row["field_value"], int(row["aggressive_negative_trade_count"])) for row in stage_gap_rows),
            key=lambda item: item[1],
            default=("none", 0),
        )
        negative_role = max(
            ((row["field_value"], int(row["aggressive_negative_trade_count"])) for row in role_gap_rows),
            key=lambda item: item[1],
            default=("none", 0),
        )
        negative_catalyst = max(
            ((row["field_value"], int(row["aggressive_negative_trade_count"])) for row in catalyst_gap_rows),
            key=lambda item: item[1],
            default=("none", 0),
        )

        margin_quality_rows = [
            {
                "bucket_name": "winning_trades",
                "trade_count": len(winner_margins),
                "average_probability_margin": round(winner_margin_mean, 4),
            },
            {
                "bucket_name": "losing_trades",
                "trade_count": len(loser_margins),
                "average_probability_margin": round(loser_margin_mean, 4),
            },
            {
                "bucket_name": "recommended_neutral_floor",
                "trade_count": len(aggressive_trades),
                "average_probability_margin": recommended_margin_floor,
            },
        ]

        recommendation_rows = [
            {
                "recommendation_name": "minimum_probability_margin_floor",
                "recommended_value": recommended_margin_floor,
                "reason": "Winning trades carry a visibly higher mean probability margin than losing trades.",
            },
            {
                "recommendation_name": "minimum_confidence_tier_numeric",
                "recommended_value": 1.0,
                "reason": "Only allow neutral participation in windows with at least ignition/main-markup confidence.",
            },
            {
                "recommendation_name": "minimum_rollforward_state_numeric",
                "recommended_value": 0.0,
                "reason": "The aggressive line gives back too much in negative rollforward windows.",
            },
            {
                "recommendation_name": "maximum_turnover_state_numeric",
                "recommended_value": 1.0,
                "reason": "The neutral line should skip the hottest board-pressure regimes instead of forcing participation.",
            },
            {
                "recommendation_name": "minimum_weighted_breadth_ratio",
                "recommended_value": 0.45,
                "reason": "Selective participation should require some minimum breadth confirmation.",
            },
            {
                "recommendation_name": "minimum_catalyst_presence_proxy",
                "recommended_value": 0.35,
                "reason": "Weak or stale catalyst states should not be enough to open a neutral position.",
            },
        ]

        oracle_total_return = float(oracle_summary.get("total_return", 0.0))
        aggressive_total_return = float(aggressive_summary.get("total_return", 0.0))
        return_capture_ratio = aggressive_total_return / oracle_total_return if oracle_total_return else 0.0
        oracle_drawdown = float(oracle_summary.get("max_drawdown", 0.0))
        aggressive_drawdown = float(aggressive_summary.get("max_drawdown", 0.0))

        summary = {
            "acceptance_posture": "freeze_v112bg_cpo_oracle_vs_no_leak_gap_review_v1",
            "oracle_trade_count": len(oracle_trades),
            "aggressive_trade_count": len(aggressive_trades),
            "return_capture_ratio": round(return_capture_ratio, 4),
            "drawdown_penalty_vs_oracle": round(abs(aggressive_drawdown) - abs(oracle_drawdown), 4),
            "primary_gap_axis": "risk_control_and_stage_maturity_filtering",
            "highest_negative_stage": negative_stage[0],
            "highest_negative_role": negative_role[0],
            "highest_negative_catalyst_bucket": negative_catalyst[0],
            "recommended_probability_margin_floor": recommended_margin_floor,
            "open_neutral_selective_track_next": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The oracle-vs-aggressive gap is too large to interpret as a simple factor omission; it also reflects drawdown control and stage-maturity filtering failures.",
            "The aggressive line is profitable, but its losses cluster in mature or conflicted windows where the neutral line should accept cash.",
            "V1.12BG therefore freezes a selective gate stack rather than pretending the aggressive objective should simply be tuned harder.",
        ]
        return V112BGCPOOracleVsNoLeakGapReviewReport(
            summary=summary,
            stage_gap_rows=stage_gap_rows,
            role_gap_rows=role_gap_rows,
            catalyst_gap_rows=catalyst_gap_rows,
            margin_quality_rows=margin_quality_rows,
            recommendation_rows=recommendation_rows,
            interpretation=interpretation,
        )

    def _dimension_gap_rows(
        self,
        *,
        oracle_trades: list[dict[str, Any]],
        aggressive_trades: list[dict[str, Any]],
        field_name: str,
    ) -> list[dict[str, Any]]:
        oracle_counter: Counter[str] = Counter()
        aggressive_counter: Counter[str] = Counter()
        aggressive_negative_counter: Counter[str] = Counter()
        aggressive_return_sum: defaultdict[str, float] = defaultdict(float)

        for row in oracle_trades:
            oracle_counter[str(row.get(field_name))] += 1
        for row in aggressive_trades:
            key = str(row.get(field_name))
            aggressive_counter[key] += 1
            realized = float(row.get("realized_forward_return_20d", 0.0))
            aggressive_return_sum[key] += realized
            if realized < 0.0:
                aggressive_negative_counter[key] += 1

        rows: list[dict[str, Any]] = []
        for field_value in sorted(set(oracle_counter) | set(aggressive_counter)):
            trade_count = int(aggressive_counter[field_value])
            rows.append(
                {
                    "field_name": field_name,
                    "field_value": field_value,
                    "oracle_trade_count": int(oracle_counter[field_value]),
                    "aggressive_trade_count": trade_count,
                    "aggressive_negative_trade_count": int(aggressive_negative_counter[field_value]),
                    "aggressive_average_return": round(aggressive_return_sum[field_value] / trade_count, 4) if trade_count else 0.0,
                }
            )
        return rows


def write_v112bg_cpo_oracle_vs_no_leak_gap_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BGCPOOracleVsNoLeakGapReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
