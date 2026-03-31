from __future__ import annotations

import json
import math
import os
from bisect import bisect_right
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
)
from a_share_quant.strategy.v112av_cpo_branch_role_geometry_patch_pilot_v1 import (
    V112AVCPOBranchRoleGeometryPatchPilotAnalyzer,
)


@dataclass(slots=True)
class V112BNTeacherDecompositionGateSearchReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "comparison_rows": self.comparison_rows,
            "plot_bundle_rows": self.plot_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


@dataclass(frozen=True, slots=True)
class RuleAtom:
    feature_name: str
    operator: str
    threshold: float
    family: str

    def signature(self) -> str:
        operator = ">=" if self.operator == "ge" else "<="
        threshold = f"{self.threshold:.4f}".rstrip("0").rstrip(".")
        return f"{self.feature_name}{operator}{threshold}"


@dataclass(frozen=True, slots=True)
class RuleSpec:
    atoms: tuple[RuleAtom, ...]
    stage_name: str

    def signature(self) -> str:
        return " & ".join(sorted(atom.signature() for atom in self.atoms))

    def feature_names(self) -> tuple[str, ...]:
        return tuple(sorted({atom.feature_name for atom in self.atoms}))


class V112BNTeacherDecompositionGateSearchAnalyzer:
    HOLDING_DAYS = 20
    MIN_TRAIN_SAMPLES = 120

    CORE_FEATURE_GRIDS: dict[str, tuple[str, tuple[float, ...]]] = {
        "probability_margin": ("ge", (0.18,)),
        "confidence_tier_numeric": ("ge", (1.0,)),
        "rollforward_state_numeric": ("ge", (0.5,)),
        "turnover_state_numeric": ("le", (0.85,)),
        "weighted_breadth_ratio": ("ge", (0.45,)),
        "catalyst_presence_proxy": ("ge", (0.35,)),
    }
    OVERLAY_FEATURE_GRIDS: dict[str, tuple[str, tuple[float, ...]]] = {
        "broad_index_trend_state": ("ge", (0.02,)),
        "risk_appetite_heat_state": ("ge", (0.02,)),
        "turnover_pressure_overlay_state": ("le", (0.05,)),
        "window_uncertainty_numeric": ("le", (0.50,)),
        "sector_rotation_conflict_state": ("le", (0.02,)),
    }
    SEARCH_TOP_CORE = 3
    SEARCH_TOP_OVERLAY = 3

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        ranker_pilot_payload: dict[str, Any],
        market_overlay_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
        v112bj_teacher_gate_payload: dict[str, Any],
    ) -> V112BNTeacherDecompositionGateSearchReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bn_now")):
            raise ValueError("V1.12BN must be open before teacher decomposition search runs.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        ranker_summary = dict(ranker_pilot_payload.get("summary", {}))
        teacher_gate_summary = dict(v112bj_teacher_gate_payload.get("summary", {}))
        market_overlay_summary = dict(market_overlay_payload.get("summary", {}))
        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BN expects the frozen 10-row training-facing layer.")
        if not bool(market_overlay_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BN expects the frozen market-regime overlay family from V1.12BD.")
        if not bool(teacher_gate_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BN expects the completed neutral teacher-gate negative control.")

        print("[v112bn] building decision frame...", flush=True)
        frame = self._build_decision_frame(
            training_layer_rows=training_layer_rows,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )
        print(f"[v112bn] decision frame rows={len(frame)} cols={len(frame.columns)}", flush=True)
        teacher_trade_rows = list(neutral_pilot_payload.get("trade_rows", []))
        teacher_entry_dates = {str(row.get("entry_date")) for row in teacher_trade_rows}
        teacher_entry_pairs = {(str(row.get("entry_date")), str(row.get("symbol"))) for row in teacher_trade_rows}
        teacher_cash_ratio = float(dict(neutral_pilot_payload.get("summary", {})).get("cash_ratio", 0.0))
        frame = frame.copy()
        frame["teacher_entry_label"] = frame["trade_date"].astype(str).isin(teacher_entry_dates).astype(int)
        teacher_pair_frame = pd.DataFrame(teacher_entry_pairs, columns=["trade_date", "symbol"]) if teacher_entry_pairs else pd.DataFrame(columns=["trade_date", "symbol"])
        if not teacher_pair_frame.empty:
            frame = frame.merge(teacher_pair_frame.assign(teacher_pair_label=1), on=["trade_date", "symbol"], how="left")
            if "teacher_pair_label" not in frame.columns:
                pair_label_col = next((name for name in frame.columns if name.startswith("teacher_pair_label")), None)
                if pair_label_col is None:
                    frame["teacher_pair_label"] = 0
                else:
                    frame["teacher_pair_label"] = frame[pair_label_col].fillna(0).astype(int)
                    if pair_label_col != "teacher_pair_label":
                        frame = frame.drop(columns=[pair_label_col])
            else:
                frame["teacher_pair_label"] = frame["teacher_pair_label"].fillna(0).astype(int)
        else:
            frame["teacher_pair_label"] = 0

        if frame.empty:
            raise ValueError("V1.12BN needs at least one teacher-decision row to search.")
        search_frame = frame[frame["trade_date"].astype(str).isin(teacher_entry_dates)].copy()
        if search_frame.empty:
            raise ValueError("V1.12BN could not isolate teacher decision dates for the bounded search.")
        frame = search_frame
        print(f"[v112bn] search frame rows={len(frame)} teacher_dates={len(teacher_entry_dates)}", flush=True)

        print("[v112bn] searching core gate space...", flush=True)
        core_candidates = self._search_rule_space(
            frame=frame,
            feature_grids=self.CORE_FEATURE_GRIDS,
            stage_name="core",
            min_size=2,
            max_size=2,
        )
        print(f"[v112bn] core candidates={len(core_candidates)}", flush=True)
        print("[v112bn] searching overlay-augmented space...", flush=True)
        overlay_candidates = self._search_overlay_augmented_space(
            frame=frame,
            base_candidates=core_candidates[: self.SEARCH_TOP_CORE],
            feature_grids=self.OVERLAY_FEATURE_GRIDS,
            stage_name="overlay_augmented",
            min_size=1,
            max_size=1,
        )
        print(f"[v112bn] overlay candidates={len(overlay_candidates)}", flush=True)

        all_candidate_rows = sorted(
            core_candidates + overlay_candidates,
            key=lambda row: self._candidate_sort_key(row, teacher_cash_ratio=teacher_cash_ratio),
            reverse=True,
        )
        print(f"[v112bn] total candidates={len(all_candidate_rows)}", flush=True)
        top_candidate_rows = [self._public_candidate_row(row) for row in all_candidate_rows[:50]]
        non_cash_candidates = [row for row in all_candidate_rows if int(row["trade_count"]) > 0]
        if non_cash_candidates:
            best_candidate = non_cash_candidates[0]
            all_non_cash_failed = False
        else:
            best_candidate = self._cash_only_baseline_row()
            all_non_cash_failed = True

        if int(best_candidate["trade_count"]) > 0:
            trade_rows, equity_curve_rows = self._simulate_portfolio(
                frame=frame,
                rule_signature=str(best_candidate["rule_signature"]),
                rule_atoms=best_candidate["rule_atoms"],
            )
        else:
            trade_rows = []
            equity_curve_rows = [{"trade_date": str(frame["trade_date"].min()), "equity": 1.0, "position_state": "cash", "symbol": "CASH"}]
        if not equity_curve_rows:
            equity_curve_rows = [{"trade_date": str(frame["trade_date"].min()), "equity": 1.0, "position_state": "cash", "symbol": "CASH"}]
        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        portfolio_metrics = self._portfolio_summary_metrics(equity_curve_rows=equity_curve_rows, trade_rows=trade_rows)

        candidate_trade_dates = {str(row["entry_date"]) for row in trade_rows}
        candidate_trade_pairs = {(str(row["entry_date"]), str(row["symbol"])) for row in trade_rows}
        date_intersection = len(candidate_trade_dates & teacher_entry_dates)
        pair_intersection = len(candidate_trade_pairs & teacher_entry_pairs)
        date_recall = date_intersection / len(teacher_entry_dates) if teacher_entry_dates else 0.0
        date_precision = date_intersection / len(candidate_trade_dates) if candidate_trade_dates else 0.0
        pair_recall = pair_intersection / len(teacher_entry_pairs) if teacher_entry_pairs else 0.0
        pair_precision = pair_intersection / len(candidate_trade_pairs) if candidate_trade_pairs else 0.0
        date_f1 = self._harmonic_mean(date_recall, date_precision) if (date_recall or date_precision) else 0.0
        pair_f1 = self._harmonic_mean(pair_recall, pair_precision) if (pair_recall or pair_precision) else 0.0
        alignment_f1 = 0.6 * date_f1 + 0.4 * pair_f1

        comparison_rows = [
            {
                "comparison_name": "return_vs_neutral",
                "neutral_value": neutral_summary.get("total_return"),
                "teacher_decomposition_value": portfolio_metrics["total_return"],
                "delta": round(portfolio_metrics["total_return"] - float(neutral_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_aggressive",
                "aggressive_value": aggressive_summary.get("total_return"),
                "teacher_decomposition_value": portfolio_metrics["total_return"],
                "delta": round(portfolio_metrics["total_return"] - float(aggressive_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_ranker",
                "ranker_value": ranker_summary.get("total_return"),
                "teacher_decomposition_value": portfolio_metrics["total_return"],
                "delta": round(portfolio_metrics["total_return"] - float(ranker_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_gap_vs_oracle",
                "oracle_value": oracle_summary.get("total_return"),
                "teacher_decomposition_value": portfolio_metrics["total_return"],
                "gap": round(float(oracle_summary.get("total_return", 0.0)) - portfolio_metrics["total_return"], 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112bn_teacher_decomposition_gate_search_v1",
            "track_name": "teacher_decomposition_gate_search_track",
            "no_leak_enforced": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": int(frame.shape[0]),
            "teacher_decision_row_count": int(frame.shape[0]),
            "candidate_row_count": len(all_candidate_rows),
            "core_candidate_count": len(core_candidates),
            "overlay_candidate_count": len(overlay_candidates),
            "non_cash_candidate_count": len(non_cash_candidates),
            "best_candidate_rule_count": len(best_candidate.get("rule_atoms", ())),
            "best_candidate_stage": str(best_candidate.get("stage", "cash_only")),
            "trade_count": int(portfolio_metrics["trade_count"]),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(portfolio_metrics["total_return"], 4),
            "max_drawdown": round(portfolio_metrics["max_drawdown"], 4),
            "profit_factor": round(portfolio_metrics["profit_factor"], 4) if portfolio_metrics["profit_factor"] != math.inf else "inf",
            "hit_rate": round(portfolio_metrics["hit_rate"], 4),
            "cash_ratio": round(portfolio_metrics["cash_ratio"], 4),
            "teacher_alignment_recall": round(date_recall, 4),
            "teacher_alignment_precision": round(date_precision, 4),
            "teacher_alignment_f1": round(alignment_f1, 4),
            "teacher_exact_alignment_recall": round(pair_recall, 4),
            "teacher_exact_alignment_precision": round(pair_precision, 4),
            "teacher_exact_alignment_f1": round(pair_f1, 4),
            "neutral_return_delta": round(portfolio_metrics["total_return"] - float(neutral_summary.get("total_return", 0.0)), 4),
            "aggressive_return_delta": round(portfolio_metrics["total_return"] - float(aggressive_summary.get("total_return", 0.0)), 4),
            "ranker_return_delta": round(portfolio_metrics["total_return"] - float(ranker_summary.get("total_return", 0.0)), 4),
            "oracle_return_gap": round(float(oracle_summary.get("total_return", 0.0)) - portfolio_metrics["total_return"], 4),
            "all_non_cash_failed_proven": all_non_cash_failed,
            "best_non_cash_candidate_found": int(best_candidate.get("trade_count", 0)) > 0,
            "best_candidate_non_cash": int(best_candidate.get("trade_count", 0)) > 0,
            "best_candidate_cash_ratio_gap_to_teacher": round(abs(portfolio_metrics["cash_ratio"] - teacher_cash_ratio), 4),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "review_best_non_cash_teacher_decomposition_candidate_and_then_decide_whether_the_gate_stack_can_be_reused"
                if int(best_candidate.get("trade_count", 0)) > 0
                else "prove_that_all_non_cash_candidates_fail_before_any_gate_stack_is_promoted"
            ),
        }

        interpretation = [
            "V1.12BN searches a bounded factorization of the current neutral selective teacher instead of training a new monolithic policy.",
            "It remains report-only and no-leak; the objective is to learn whether the neutral gate can be approximated by a small conjunction of quantized conditions.",
            "A non-cash decomposition that materially improves teacher alignment would suggest the teacher is factorable; otherwise the neutral line is dominated by a harder-to-factor decision surface.",
        ]

        return V112BNTeacherDecompositionGateSearchReport(
            summary=summary,
            candidate_rows=top_candidate_rows,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            comparison_rows=comparison_rows,
            plot_bundle_rows=[
                {"plot_name": "teacher_decomposition_equity_curve", "series_name": "equity", "point_count": len(equity_curve_rows)},
                {"plot_name": "teacher_decomposition_drawdown_curve", "series_name": "drawdown", "point_count": len(drawdown_curve_rows)},
            ],
            interpretation=interpretation,
        )

    def _build_decision_frame(
        self,
        *,
        training_layer_rows: list[dict[str, Any]],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> pd.DataFrame:
        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        role_patch = V112AOCPORoleLayerPatchPilotAnalyzer()
        branch_patch = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in training_layer_rows}
        impl_features = widen_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001
        feature_names = (
            list(pilot_analyzer.FEATURE_NAMES)
            + list(role_patch.PATCH_FEATURE_NAMES)
            + list(widen_analyzer.IMPLEMENTATION_FEATURE_NAMES)
            + list(branch_patch.BRANCH_PATCH_FEATURE_NAMES)
        )

        sample_rows: list[dict[str, Any]] = []
        for sample in samples:
            row = {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage_family": sample.stage_family,
                "role_family": sample.role_family,
                "catalyst_sequence_label": sample.catalyst_sequence_label,
                "forward_return_20d": float(sample.forward_return_20d),
                "max_drawdown_20d": float(sample.max_drawdown_20d),
            }
            for name in pilot_analyzer.FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in role_patch.PATCH_FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES:
                row[name] = float(impl_features[(sample.trade_date, sample.symbol)][name])
            branch_values = branch_patch._branch_patch_values(sample=sample)  # noqa: SLF001
            for idx, name in enumerate(branch_patch.BRANCH_PATCH_FEATURE_NAMES):
                row[name] = float(branch_values[idx])
            sample_rows.append(row)

        frame = pd.DataFrame(sample_rows).sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        frame = frame.copy()
        frame["winner_label"] = 0
        for _, group in frame.groupby("trade_date"):
            positive = group[group["forward_return_20d"] > 0.0]
            if positive.empty:
                continue
            winner_idx = int(positive["forward_return_20d"].idxmax())
            frame.loc[winner_idx, "winner_label"] = 1

        teacher_proxy_rows = self._build_teacher_proxy_rows(frame=frame, feature_names=feature_names)
        proxy_frame = pd.DataFrame(teacher_proxy_rows).sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        proxy_frame = self._market_overlay_backfill(proxy_frame)
        return proxy_frame

    def _build_teacher_proxy_rows(self, *, frame: pd.DataFrame, feature_names: list[str]) -> list[dict[str, Any]]:
        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        rows: list[dict[str, Any]] = []
        for idx, trade_date in enumerate(ordered_dates):
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0:
                continue
            cutoff_date = ordered_dates[decision_idx]
            train_frame = frame[frame["trade_date"] <= cutoff_date].copy()
            current_frame = frame[frame["trade_date"] == trade_date].copy()
            if len(train_frame) < self.MIN_TRAIN_SAMPLES:
                continue
            training_base_rate = float(train_frame["winner_label"].mean()) if not train_frame.empty else 0.0
            proxy_score = (
                0.22 * current_frame["catalyst_presence_proxy"]
                + 0.18 * current_frame["weighted_breadth_ratio"]
                + 0.16 * current_frame["confidence_tier_numeric"]
                + 0.12 * current_frame["rollforward_state_numeric"].clip(lower=0.0)
                - 0.18 * current_frame["turnover_state_numeric"]
                - 0.08 * current_frame["window_uncertainty_numeric"]
                - 0.06 * current_frame["realized_vol_10"]
                - 0.05 * current_frame["volume_cv_10"]
            )
            proxy_score = proxy_score.fillna(0.0).astype(float)
            winner_prob = 1.0 / (1.0 + np.exp(-proxy_score.to_numpy(dtype=float)))
            current_frame["winner_prob"] = winner_prob
            current_frame["probability_margin"] = current_frame["winner_prob"] - training_base_rate
            current_frame["selective_score"] = (
                current_frame["probability_margin"]
                + 0.08 * current_frame["catalyst_presence_proxy"]
                + 0.06 * current_frame["weighted_breadth_ratio"]
                + 0.04 * current_frame["confidence_tier_numeric"]
                + 0.03 * current_frame["rollforward_state_numeric"].clip(lower=0.0)
                - 0.05 * current_frame["turnover_state_numeric"]
                - 0.03 * current_frame["window_uncertainty_numeric"]
                - 0.02 * current_frame["realized_vol_10"]
                - 0.02 * current_frame["volume_cv_10"]
            )
            current_frame["teacher_entry_label"] = 0
            current_frame["teacher_pair_label"] = 0
            rows.extend(current_frame.to_dict("records"))
        return rows

    def _market_overlay_backfill(self, frame: pd.DataFrame) -> pd.DataFrame:
        dates = sorted(frame["trade_date"].unique().tolist())
        if not dates:
            return frame
        overlay_frame = self._build_market_overlay_frame(dates)
        merged = frame.merge(overlay_frame, on="trade_date", how="left")
        for name in self.OVERLAY_FEATURE_GRIDS:
            if name in merged.columns:
                merged[name] = merged[name].fillna(0.0)
        return merged

    def _build_market_overlay_frame(self, dates: list[str]) -> pd.DataFrame:
        client = TencentKlineClient()
        symbols = ["000001", "399001", "399006", "000688", "510050", "512760"]
        frames: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            bars = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            bars["trade_date"] = pd.to_datetime(bars["date"]).dt.strftime("%Y-%m-%d")
            bars["close"] = bars["close"].astype(float)
            bars["volume"] = bars["volume"].astype(float)
            for window in (5, 10, 20):
                bars[f"ret_{window}"] = bars["close"].pct_change(window)
            bars["volume_z_20"] = (bars["volume"] - bars["volume"].rolling(20).mean()) / bars["volume"].rolling(20).std(ddof=0)
            frames[symbol] = bars[["trade_date", "ret_5", "ret_10", "ret_20", "volume_z_20"]].copy()

        merged = frames[symbols[0]].rename(
            columns={
                "ret_5": f"{symbols[0]}_ret_5",
                "ret_10": f"{symbols[0]}_ret_10",
                "ret_20": f"{symbols[0]}_ret_20",
                "volume_z_20": f"{symbols[0]}_volume_z_20",
            }
        )
        for symbol in symbols[1:]:
            renamed = frames[symbol].rename(
                columns={
                    "ret_5": f"{symbol}_ret_5",
                    "ret_10": f"{symbol}_ret_10",
                    "ret_20": f"{symbol}_ret_20",
                    "volume_z_20": f"{symbol}_volume_z_20",
                }
            )
            merged = merged.merge(renamed, on="trade_date", how="outer")
        merged = merged.sort_values("trade_date").reset_index(drop=True)

        def _mean_cols(row: pd.Series, cols: list[str]) -> float:
            values = [float(row[c]) for c in cols if pd.notna(row.get(c))]
            return float(np.mean(values)) if values else 0.0

        def _std_cols(row: pd.Series, cols: list[str]) -> float:
            values = [float(row[c]) for c in cols if pd.notna(row.get(c))]
            return float(np.std(values, ddof=0)) if values else 0.0

        overlay_rows: list[dict[str, Any]] = []
        for _, row in merged.iterrows():
            broad_trend = _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001", "510050"]])
            liquidity = _mean_cols(row, [f"{s}_volume_z_20" for s in ["000001", "399001", "510050"]])
            risk_heat = _mean_cols(row, [f"{s}_ret_20" for s in ["399006", "000688", "512760"]]) - _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001"]])
            chinext_strength = float(row.get("399006_ret_20", 0.0)) - _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001"]])
            star_strength = float(row.get("000688_ret_20", 0.0)) - _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001"]])
            optics_strength = float(row.get("512760_ret_20", 0.0)) - _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001"]])
            turnover_pressure = _mean_cols(row, [f"{s}_volume_z_20" for s in ["000001", "399001"]])
            liquidity_dispersion = _std_cols(row, [f"{s}_ret_20" for s in ["000001", "399001", "399006", "000688", "510050", "512760"]])
            rotation_conflict = abs(float(row.get("399006_ret_20", 0.0)) - float(row.get("000688_ret_20", 0.0))) + abs(float(row.get("512760_ret_20", 0.0)) - _mean_cols(row, [f"{s}_ret_20" for s in ["000001", "399001"]]))
            overlay_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "broad_index_trend_state": broad_trend,
                    "all_market_turnover_liquidity_state": liquidity,
                    "risk_appetite_heat_state": risk_heat,
                    "chinext_relative_strength_state": chinext_strength,
                    "star_board_relative_strength_state": star_strength,
                    "optics_sector_etf_strength_state": optics_strength,
                    "turnover_pressure_overlay_state": turnover_pressure,
                    "liquidity_dispersion_state": liquidity_dispersion,
                    "sector_rotation_conflict_state": rotation_conflict,
                }
            )

        overlay_frame = pd.DataFrame(overlay_rows)
        overlay_frame = overlay_frame[overlay_frame["trade_date"].isin(dates)].copy()
        overlay_frame = overlay_frame.sort_values("trade_date").reset_index(drop=True)
        return overlay_frame

    def _search_rule_space(
        self,
        *,
        frame: pd.DataFrame,
        feature_grids: dict[str, tuple[str, tuple[float, ...]]],
        stage_name: str,
        min_size: int,
        max_size: int,
    ) -> list[dict[str, Any]]:
        feature_names = list(feature_grids.keys())
        all_candidate_rows: list[dict[str, Any]] = []
        for size in range(min_size, max_size + 1):
            for feature_subset in combinations(feature_names, size):
                threshold_lists = [feature_grids[feature_name][1] for feature_name in feature_subset]
                for threshold_combo in product(*threshold_lists):
                    atoms = tuple(
                        RuleAtom(
                            feature_name=feature_name,
                            operator=feature_grids[feature_name][0],
                            threshold=float(threshold),
                            family=stage_name,
                        )
                        for feature_name, threshold in zip(feature_subset, threshold_combo, strict=True)
                    )
                    spec = RuleSpec(atoms=atoms, stage_name=stage_name)
                    metrics = self._evaluate_rule_spec(frame=frame, spec=spec)
                    all_candidate_rows.append(metrics)
        all_candidate_rows.sort(key=lambda row: self._candidate_sort_key(row), reverse=True)
        return all_candidate_rows

    def _search_overlay_augmented_space(
        self,
        *,
        frame: pd.DataFrame,
        base_candidates: list[dict[str, Any]],
        feature_grids: dict[str, tuple[str, tuple[float, ...]]],
        stage_name: str,
        min_size: int,
        max_size: int,
    ) -> list[dict[str, Any]]:
        overlay_rows: list[dict[str, Any]] = []
        for base_row in base_candidates:
            base_atoms = tuple(base_row["rule_atoms"])
            used_features = {atom.feature_name for atom in base_atoms}
            remaining_features = [name for name in feature_grids if name not in used_features]
            for size in range(min_size, max_size + 1):
                for feature_subset in combinations(remaining_features, size):
                    threshold_lists = [feature_grids[feature_name][1] for feature_name in feature_subset]
                    for threshold_combo in product(*threshold_lists):
                        overlay_atoms = tuple(
                            RuleAtom(
                                feature_name=feature_name,
                                operator=feature_grids[feature_name][0],
                                threshold=float(threshold),
                                family=stage_name,
                            )
                            for feature_name, threshold in zip(feature_subset, threshold_combo, strict=True)
                        )
                        spec = RuleSpec(atoms=base_atoms + overlay_atoms, stage_name=stage_name)
                        metrics = self._evaluate_rule_spec(frame=frame, spec=spec)
                        overlay_rows.append(metrics)
        overlay_rows.sort(key=lambda row: self._candidate_sort_key(row), reverse=True)
        return overlay_rows

    def _evaluate_rule_spec(self, *, frame: pd.DataFrame, spec: RuleSpec) -> dict[str, Any]:
        frame = frame.copy().sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        atom_masks = {atom.signature(): self._atom_mask(frame=frame, atom=atom) for atom in spec.atoms}
        candidate_mask = np.ones(len(frame), dtype=bool)
        for atom in spec.atoms:
            candidate_mask &= atom_masks[atom.signature()]

        if not candidate_mask.any():
            return self._candidate_metrics_row(
                frame=frame,
                spec=spec,
                trade_rows=[],
                equity_curve_rows=[{"trade_date": str(frame["trade_date"].min()), "equity": 1.0, "position_state": "cash", "symbol": "CASH"}],
                cash_only=True,
            )

        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        date_groups = {trade_date: frame.index[frame["trade_date"] == trade_date].to_numpy(dtype=int) for trade_date in ordered_dates}
        bar_cache = self._bar_cache(symbols=sorted(frame["symbol"].unique().tolist()))
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0
        selective_scores = frame["selective_score"].to_numpy(dtype=float)

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0 or trade_date not in date_groups:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            current_indices = date_groups[trade_date]
            allowed_indices = current_indices[candidate_mask[current_indices]]
            if len(allowed_indices) == 0:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            best_idx = int(allowed_indices[np.argmax(selective_scores[allowed_indices])])
            chosen_row = frame.loc[best_idx]
            trade_path = self._trade_path(symbol=str(chosen_row["symbol"]), entry_date=trade_date, bars=bar_cache[str(chosen_row["symbol"])])
            if not trade_path:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            entry_equity = current_equity
            path_peak = entry_equity
            max_path_drawdown = 0.0
            for row in trade_path:
                path_equity = entry_equity * float(row["price_ratio"])
                path_peak = max(path_peak, path_equity)
                if path_peak > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / path_peak - 1.0)
                self._append_equity_point(equity_curve_rows, str(row["trade_date"]), path_equity, "long", str(chosen_row["symbol"]))
            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": trade_date,
                    "exit_date": exit_date,
                    "symbol": str(chosen_row["symbol"]),
                    "stage_family": str(chosen_row["stage_family"]),
                    "role_family": str(chosen_row["role_family"]),
                    "catalyst_sequence_label": str(chosen_row["catalyst_sequence_label"]),
                    "rule_signature": spec.signature(),
                    "rule_depth": len(spec.atoms),
                    "teacher_selective_score": round(float(chosen_row["selective_score"]), 4),
                    "winner_prob": round(float(chosen_row["winner_prob"]), 4),
                    "probability_margin": round(float(chosen_row["probability_margin"]), 4),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(chosen_row["forward_return_20d"]), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        return self._candidate_metrics_row(
            frame=frame,
            spec=spec,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            cash_only=False,
        )

    def _candidate_metrics_row(
        self,
        *,
        frame: pd.DataFrame,
        spec: RuleSpec,
        trade_rows: list[dict[str, Any]],
        equity_curve_rows: list[dict[str, Any]],
        cash_only: bool,
    ) -> dict[str, Any]:
        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")
        teacher_entry_dates = set(frame.loc[frame["teacher_entry_label"] == 1, "trade_date"].astype(str).tolist())
        teacher_pair_frame = frame[frame["teacher_pair_label"] == 1]
        teacher_entry_pairs = set(zip(teacher_pair_frame["trade_date"].astype(str).tolist(), teacher_pair_frame["symbol"].astype(str).tolist(), strict=False))
        candidate_entry_dates = {str(row["entry_date"]) for row in trade_rows}
        candidate_entry_pairs = {(str(row["entry_date"]), str(row["symbol"])) for row in trade_rows}
        date_intersection = len(candidate_entry_dates & teacher_entry_dates)
        pair_intersection = len(candidate_entry_pairs & teacher_entry_pairs)
        date_recall = date_intersection / len(teacher_entry_dates) if teacher_entry_dates else 0.0
        date_precision = date_intersection / len(candidate_entry_dates) if candidate_entry_dates else 0.0
        pair_recall = pair_intersection / len(teacher_entry_pairs) if teacher_entry_pairs else 0.0
        pair_precision = pair_intersection / len(candidate_entry_pairs) if candidate_entry_pairs else 0.0
        date_f1 = self._harmonic_mean(date_recall, date_precision) if (date_recall or date_precision) else 0.0
        pair_f1 = self._harmonic_mean(pair_recall, pair_precision) if (pair_recall or pair_precision) else 0.0
        alignment_f1 = 0.6 * date_f1 + 0.4 * pair_f1
        return {
            "stage": spec.stage_name,
            "rule_signature": spec.signature(),
            "rule_atoms": spec.atoms,
            "rule_depth": len(spec.atoms),
            "feature_names": spec.feature_names(),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "teacher_alignment_recall": round(float(date_recall), 4),
            "teacher_alignment_precision": round(float(date_precision), 4),
            "teacher_exact_alignment_recall": round(float(pair_recall), 4),
            "teacher_exact_alignment_precision": round(float(pair_precision), 4),
            "teacher_alignment_f1": round(float(alignment_f1), 4),
            "teacher_date_f1": round(float(date_f1), 4),
            "teacher_pair_f1": round(float(pair_f1), 4),
            "cash_only": cash_only,
        }

    def _cash_only_baseline_row(self) -> dict[str, Any]:
        return {
            "stage": "cash_only",
            "rule_signature": "CASH_ONLY",
            "rule_atoms": tuple(),
            "rule_depth": 0,
            "feature_names": tuple(),
            "trade_count": 0,
            "equity_curve_point_count": 1,
            "drawdown_curve_point_count": 1,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "profit_factor": "inf",
            "hit_rate": 0.0,
            "cash_ratio": 1.0,
            "teacher_alignment_recall": 0.0,
            "teacher_alignment_precision": 0.0,
            "teacher_exact_alignment_recall": 0.0,
            "teacher_exact_alignment_precision": 0.0,
            "teacher_alignment_f1": 0.0,
            "teacher_date_f1": 0.0,
            "teacher_pair_f1": 0.0,
            "cash_only": True,
        }

    def _atom_mask(self, *, frame: pd.DataFrame, atom: RuleAtom) -> np.ndarray:
        values = frame[atom.feature_name].astype(float).to_numpy(dtype=float)
        if atom.operator == "ge":
            return values >= float(atom.threshold)
        if atom.operator == "le":
            return values <= float(atom.threshold)
        raise ValueError(f"Unsupported operator {atom.operator!r}.")

    def _candidate_sort_key(self, row: dict[str, Any], *, teacher_cash_ratio: float = 0.0) -> tuple[float, ...]:
        trade_count = int(row.get("trade_count", 0))
        non_cash = 1.0 if trade_count > 0 else 0.0
        return (
            non_cash,
            float(row.get("teacher_alignment_f1", 0.0)),
            float(row.get("teacher_date_f1", 0.0)),
            float(row.get("teacher_pair_f1", 0.0)),
            float(row.get("total_return", 0.0)),
            -abs(float(row.get("max_drawdown", 0.0))),
            -abs(float(row.get("cash_ratio", 0.0)) - float(teacher_cash_ratio)),
            float(row.get("trade_count", 0)),
        )

    def _public_candidate_row(self, row: dict[str, Any]) -> dict[str, Any]:
        public_row = dict(row)
        atoms = public_row.pop("rule_atoms", tuple())
        public_row["rule_atom_signatures"] = [atom.signature() for atom in atoms]
        public_row.pop("trade_rows", None)
        public_row.pop("equity_curve_rows", None)
        public_row.pop("drawdown_curve_rows", None)
        return public_row

    def _portfolio_summary_metrics(self, *, equity_curve_rows: list[dict[str, Any]], trade_rows: list[dict[str, Any]]) -> dict[str, float]:
        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")
        cash_ratio = float(cash_days / len(equity_curve_rows)) if equity_curve_rows else 0.0
        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "profit_factor": profit_factor,
            "hit_rate": hit_rate,
            "cash_ratio": cash_ratio,
            "trade_count": float(len(trade_rows)),
        }

    def _harmonic_mean(self, a: float, b: float) -> float:
        if a <= 0.0 or b <= 0.0:
            return 0.0
        return 2.0 * a * b / (a + b)

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: pd.DataFrame) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + self.HOLDING_DAYS
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows: list[dict[str, Any]] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows

    def _append_equity_point(
        self,
        equity_curve_rows: list[dict[str, Any]],
        trade_date: str,
        equity: float,
        position_state: str,
        symbol: str,
    ) -> None:
        row = {
            "trade_date": trade_date,
            "equity": round(float(equity), 6),
            "position_state": position_state,
            "symbol": symbol,
        }
        if equity_curve_rows and str(equity_curve_rows[-1]["trade_date"]) == trade_date:
            equity_curve_rows[-1] = row
        else:
            equity_curve_rows.append(row)

    def _drawdown_curve(self, equity_curve_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows: list[dict[str, Any]] = []
        for row in equity_curve_rows:
            equity = float(row["equity"])
            peak = max(peak, equity)
            drawdown = equity / peak - 1.0 if peak > 0.0 else 0.0
            rows.append({"trade_date": str(row["trade_date"]), "drawdown": round(float(drawdown), 6)})
        return rows

    def _next_index_after_exit(self, *, ordered_dates: list[str], exit_date: str) -> int:
        return bisect_right(ordered_dates, exit_date)


def write_v112bn_teacher_decomposition_gate_search_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BNTeacherDecompositionGateSearchReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
