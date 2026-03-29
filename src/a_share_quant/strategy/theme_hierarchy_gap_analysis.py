from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from a_share_quant.common.config import merge_config
from a_share_quant.common.models import DailyBar, MainlineWindow, StockSnapshot
from a_share_quant.strategy.baseline_capture_diagnostic import load_json_report
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner
from a_share_quant.strategy.rule_sweep import RuleCandidate


@dataclass(slots=True)
class ThemeHierarchyGapResult:
    summary: dict[str, Any]
    blocker_summary: dict[str, int]
    reason_transition_summary: dict[str, int]
    top_gap_days: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "blocker_summary": self.blocker_summary,
            "reason_transition_summary": self.reason_transition_summary,
            "top_gap_days": self.top_gap_days,
        }


class ThemeHierarchyGapAnalyzer:
    """Explain which hierarchy thresholds or reasons block theme late-mover admission."""

    def analyze(
        self,
        *,
        dataset_pack: DatasetPack,
        strategy_name: str,
        candidates: list[RuleCandidate],
        incumbent_name: str,
        challenger_name: str,
        admissibility_report_path: Path,
        lookback_days: int,
        engine,
        top_k: int = 30,
    ) -> ThemeHierarchyGapResult:
        admissibility_payload = load_json_report(admissibility_report_path)
        impacted_window_ids = {
            str(item["window_id"])
            for item in admissibility_payload.get("top_window_gaps", [])
            if isinstance(item, dict)
        }
        windows_by_id = {window.window_id: window for window in dataset_pack.mainline_windows}
        target_windows = [
            windows_by_id[window_id]
            for window_id in sorted(impacted_window_ids)
            if window_id in windows_by_id
        ]

        bars_by_symbol = self._bars_by_symbol(dataset_pack.bars)
        snapshot_lookup = {
            (snapshot.trade_date, snapshot.symbol): snapshot
            for snapshot in dataset_pack.stock_snapshots
        }
        strategy_states: dict[str, dict[tuple[date, str], dict[str, Any]]] = {}
        hierarchy_configs: dict[str, Any] = {}
        for candidate in candidates:
            merged_config = merge_config(dataset_pack.config, candidate.override)
            runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
            strategy_states[candidate.candidate_name] = self._collect_state(
                dataset_pack=dataset_pack,
                runner=runner,
                strategy_name=strategy_name,
                target_windows=target_windows,
                lookback_days=lookback_days,
                bars_by_symbol=bars_by_symbol,
            )
            hierarchy_configs[candidate.candidate_name] = runner.hierarchy_ranker.config

        incumbent_state = strategy_states[incumbent_name]
        challenger_state = strategy_states[challenger_name]
        incumbent_cfg = hierarchy_configs[incumbent_name]
        challenger_cfg = hierarchy_configs[challenger_name]

        gap_days: list[dict[str, Any]] = []
        blocker_summary: dict[str, int] = {}
        reason_transition_summary: dict[str, int] = {}
        for window in target_windows:
            for trade_date in self._window_dates(window=window, lookback_days=lookback_days):
                key = (trade_date, window.symbol)
                incumbent_day = incumbent_state.get(key)
                challenger_day = challenger_state.get(key)
                snapshot = snapshot_lookup.get(key)
                if incumbent_day is None or challenger_day is None or snapshot is None:
                    continue
                if not challenger_day["permission_allowed"]:
                    continue
                if not challenger_day["sector_matches_permission"]:
                    continue
                if not challenger_day["has_confirmation"]:
                    continue
                challenger_assignment = challenger_day["assignment"]
                incumbent_assignment = incumbent_day["assignment"]
                if challenger_assignment is None or incumbent_assignment is None:
                    continue
                if challenger_assignment.layer != "junk":
                    continue
                if incumbent_assignment.layer != "late_mover":
                    continue

                blocker_flags = self._blocker_flags(
                    snapshot=snapshot,
                    challenger_assignment=challenger_assignment,
                    incumbent_assignment=incumbent_assignment,
                    challenger_cfg=challenger_cfg,
                    incumbent_cfg=incumbent_cfg,
                )
                reason_transition = f"{incumbent_assignment.reason} -> {challenger_assignment.reason}"
                reason_transition_summary[reason_transition] = (
                    reason_transition_summary.get(reason_transition, 0) + 1
                )
                for flag in blocker_flags:
                    blocker_summary[flag] = blocker_summary.get(flag, 0) + 1

                gap_days.append(
                    {
                        "window_id": window.window_id,
                        "symbol": window.symbol,
                        "trade_date": trade_date.isoformat(),
                        "start_date": window.start_date.isoformat(),
                        "end_date": window.end_date.isoformat(),
                        "capturable_return": round(window.capturable_return, 6),
                        "incumbent_layer": incumbent_assignment.layer,
                        "challenger_layer": challenger_assignment.layer,
                        "incumbent_reason": incumbent_assignment.reason,
                        "challenger_reason": challenger_assignment.reason,
                        "incumbent_layer_score": round(incumbent_assignment.layer_score, 6),
                        "challenger_layer_score": round(challenger_assignment.layer_score, 6),
                        "incumbent_late_score": round(incumbent_assignment.late_score, 6),
                        "challenger_late_score": round(challenger_assignment.late_score, 6),
                        "late_mover_quality": round(snapshot.late_mover_quality, 6),
                        "resonance": round(snapshot.resonance, 6),
                        "expected_upside": round(snapshot.expected_upside, 6),
                        "stability": round(snapshot.stability, 6),
                        "liquidity": round(snapshot.liquidity, 6),
                        "passed_filters": challenger_day["passed_filters"],
                        "triggered_entries": challenger_day["triggered_entries"],
                        "blocker_flags": blocker_flags,
                    }
                )

        gap_days = sorted(
            gap_days,
            key=lambda item: (-float(item["challenger_late_score"]), -float(item["late_mover_quality"])),
        )
        summary = {
            "dataset_name": dataset_pack.dataset_name,
            "strategy_name": strategy_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "impacted_window_count": len(target_windows),
            "gap_day_count": len(gap_days),
            "unique_symbol_count": len({item["symbol"] for item in gap_days}),
            "windows_with_gap_days": len({item["window_id"] for item in gap_days}),
            "top_blocker": max(blocker_summary.items(), key=lambda item: item[1])[0] if blocker_summary else None,
            "top_reason_transition": max(reason_transition_summary.items(), key=lambda item: item[1])[0] if reason_transition_summary else None,
            "mean_late_mover_quality": round(
                sum(float(item["late_mover_quality"]) for item in gap_days) / len(gap_days),
                6,
            ) if gap_days else 0.0,
            "mean_challenger_late_score": round(
                sum(float(item["challenger_late_score"]) for item in gap_days) / len(gap_days),
                6,
            ) if gap_days else 0.0,
        }
        return ThemeHierarchyGapResult(
            summary=summary,
            blocker_summary=dict(sorted(blocker_summary.items(), key=lambda item: (-item[1], item[0]))),
            reason_transition_summary=dict(
                sorted(reason_transition_summary.items(), key=lambda item: (-item[1], item[0]))
            ),
            top_gap_days=gap_days[:top_k],
        )

    def _collect_state(
        self,
        *,
        dataset_pack: DatasetPack,
        runner: StrategyExperimentRunner,
        strategy_name: str,
        target_windows: list[MainlineWindow],
        lookback_days: int,
        bars_by_symbol: dict[str, list[DailyBar]],
    ) -> dict[tuple[date, str], dict[str, Any]]:
        strategy = runner._strategy_from_name(strategy_name)
        sector_scores = runner.scorer.score(dataset_pack.sector_snapshots)
        segments = runner._build_segments(sector_scores=sector_scores, index_bars=dataset_pack.index_bars or [])
        permissions = runner.permission_engine.evaluate(sector_scores, segments)
        allowed_sector_ids = {
            permission.approved_sector_id
            for permission in permissions
            if permission.is_attack_allowed and permission.approved_sector_id is not None
        }
        assignments = runner.hierarchy_ranker.rank(
            dataset_pack.stock_snapshots,
            allowed_sector_ids=allowed_sector_ids or None,
        )
        assignment_lookup = {
            (assignment.trade_date, assignment.symbol): assignment
            for assignment in assignments
        }
        windows_by_symbol: dict[str, list[MainlineWindow]] = {}
        for window in target_windows:
            windows_by_symbol.setdefault(window.symbol, []).append(window)

        states: dict[tuple[date, str], dict[str, Any]] = {}
        for trade_date in sorted({permission.trade_date for permission in permissions}):
            permission = strategy._permission_for_date(permissions, trade_date)
            for symbol, windows in windows_by_symbol.items():
                if not any(
                    self._in_observation_range(trade_date=trade_date, window=window, lookback_days=lookback_days)
                    for window in windows
                ):
                    continue
                symbol_bars = strategy._bars_until_date(bars_by_symbol.get(symbol, []), trade_date)
                if not symbol_bars:
                    continue
                assignment = assignment_lookup.get((trade_date, symbol))
                filters = strategy.trend_filters.evaluate(symbol_bars)
                entries = strategy.entry_rules.evaluate(symbol_bars)
                states[(trade_date, symbol)] = {
                    "permission_allowed": permission.is_attack_allowed,
                    "sector_matches_permission": (
                        assignment is not None
                        and permission.approved_sector_id is not None
                        and assignment.sector_id == permission.approved_sector_id
                    ),
                    "assignment": assignment,
                    "passed_filters": [item.filter_name for item in filters if item.passed],
                    "triggered_entries": [item.rule_name for item in entries if item.triggered],
                    "has_confirmation": any(item.passed for item in filters) and any(item.triggered for item in entries),
                }
        return states

    def _blocker_flags(
        self,
        *,
        snapshot: StockSnapshot,
        challenger_assignment,
        incumbent_assignment,
        challenger_cfg,
        incumbent_cfg,
    ) -> list[str]:
        flags: list[str] = []
        composite_score = max(
            float(challenger_assignment.leader_score),
            float(challenger_assignment.core_score),
            float(challenger_assignment.late_score),
        )
        if snapshot.late_mover_quality < challenger_cfg.min_quality_for_late_mover:
            flags.append("late_quality_below_challenger_threshold")
            if snapshot.late_mover_quality >= incumbent_cfg.min_quality_for_late_mover:
                flags.append("late_quality_in_incumbent_only_band")
        if composite_score < challenger_cfg.min_composite_for_non_junk:
            flags.append("composite_below_challenger_threshold")
            if composite_score >= incumbent_cfg.min_composite_for_non_junk:
                flags.append("composite_in_incumbent_only_band")
        if snapshot.resonance < 0.40:
            flags.append("below_global_resonance_floor")
        if challenger_assignment.reason == "fallback_to_junk":
            flags.append("fallback_to_junk_path")
        if challenger_assignment.reason == "low_composite_or_low_resonance":
            flags.append("low_composite_or_low_resonance_path")
        if incumbent_assignment.reason == "late_mover_quality_fallback":
            flags.append("incumbent_used_late_mover_fallback")
        return sorted(set(flags))

    def _bars_by_symbol(self, bars: list[DailyBar]) -> dict[str, list[DailyBar]]:
        grouped: dict[str, list[DailyBar]] = {}
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            grouped.setdefault(bar.symbol, []).append(bar)
        return grouped

    def _window_dates(self, *, window: MainlineWindow, lookback_days: int) -> list[date]:
        dates: list[date] = []
        current = window.start_date - timedelta(days=lookback_days)
        while current <= window.end_date:
            dates.append(current)
            current += timedelta(days=1)
        return dates

    def _in_observation_range(self, *, trade_date: date, window: MainlineWindow, lookback_days: int) -> bool:
        return window.start_date - timedelta(days=lookback_days) <= trade_date <= window.end_date


def write_theme_hierarchy_gap_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ThemeHierarchyGapResult,
    extras: dict[str, Any] | None = None,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    payload = result.as_dict()
    if extras:
        payload["extras"] = extras
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return output_path
