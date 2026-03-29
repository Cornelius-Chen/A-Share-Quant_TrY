from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.config import load_yaml_config, merge_config
from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_mainline_windows_from_csv,
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.data.universe import UniverseFilter
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.rule_sweep import RuleCandidate
from a_share_quant.strategy.symbol_timeline_replay import SymbolTimelineReplay


@dataclass(slots=True)
class FeaturePackBHierarchyApprovalSweepReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackBHierarchyApprovalSweepAnalyzer:
    """Sweep a few pocket-local hierarchy/approval repairs before any branch-level change."""

    def analyze(
        self,
        *,
        timeline_config_path: Path,
        case_report_path: Path,
        candidates_spec: list[dict[str, Any]],
        control_candidate_name: str,
    ) -> FeaturePackBHierarchyApprovalSweepReport:
        timeline_config = load_yaml_config(timeline_config_path)
        dataset_config = load_yaml_config(Path(str(timeline_config["dataset"]["config_path"])))
        dataset_pack = self._build_dataset_pack(timeline_config=timeline_config, dataset_config=dataset_config)
        engine = BacktestEngine(
            initial_cash=float(timeline_config["backtest"]["initial_cash"]),
            cost_model=CostModel.from_config(timeline_config["cost_model"]),
            limit_model=LimitModel.from_config(timeline_config["limit_model"]),
            price_field=str(timeline_config["backtest"].get("price_field", "open")),
        )

        base_candidates = {
            str(item["candidate_name"]): item
            for item in timeline_config.get("candidates", [])
        }
        candidates = [self._resolve_candidate(base_candidates, item) for item in candidates_spec]
        case_payload = load_json_report(case_report_path)
        case_rows = list(case_payload.get("case_row", {}).get("rows", []))
        trigger_dates = sorted({str(row["trigger_date"]) for row in case_rows})

        replay = SymbolTimelineReplay().analyze(
            dataset_pack=dataset_pack,
            strategy_names=[str(item) for item in timeline_config["strategy"]["strategy_names"]],
            candidates=candidates,
            symbol=str(timeline_config["analysis"]["symbol"]),
            start_date=date.fromisoformat(str(timeline_config["analysis"]["start_date"])),
            end_date=date.fromisoformat(str(timeline_config["analysis"]["end_date"])),
            incumbent_name=str(timeline_config["comparison"]["incumbent_candidate"]),
            challenger_name=control_candidate_name,
            engine=engine,
        )

        candidate_records = {
            str(record["candidate_name"]): record
            for record in replay.candidate_records
        }
        control_record = candidate_records[control_candidate_name]
        control_daily = {str(row["trade_date"]): row for row in control_record.get("daily_records", [])}

        candidate_rows = []
        for candidate in candidates:
            record = candidate_records[candidate.candidate_name]
            daily = {str(row["trade_date"]): row for row in record.get("daily_records", [])}
            total_pnl = round(sum(float(item["pnl"]) for item in record.get("closed_trades", [])), 6)
            candidate_rows.append(
                self._candidate_row(
                    candidate_name=candidate.candidate_name,
                    daily=daily,
                    control_daily=control_daily,
                    trigger_dates=trigger_dates,
                    total_pnl=total_pnl,
                    trade_count=len(record.get("closed_trades", [])),
                    fill_count=len(record.get("fills", [])),
                )
            )

        candidate_rows.sort(
            key=lambda row: (
                -int(row["combined_repairs"]),
                -int(row["permission_repairs"]),
                -int(row["assignment_repairs"]),
                -float(row["total_pnl"]),
            )
        )
        summary = {
            "candidate_count": len(candidate_rows),
            "trigger_date_count": len(trigger_dates),
            "best_candidate": candidate_rows[0]["candidate_name"] if candidate_rows else None,
            "best_candidate_reason": candidate_rows[0]["repair_profile"] if candidate_rows else None,
        }
        interpretation = [
            "A useful pocket-local repair should fix trigger-date states first; raw PnL alone is not enough.",
            "Permission repairs matter most on the dates where the control candidate actually lost approval.",
            "Assignment repairs matter most on the dates where the control candidate stayed in junk while the incumbent did not.",
        ]
        return FeaturePackBHierarchyApprovalSweepReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )

    def _build_dataset_pack(self, *, timeline_config: dict[str, Any], dataset_config: dict[str, Any]) -> DatasetPack:
        bars = load_daily_bars_from_csv(Path(dataset_config["paths"]["bars_csv"]))
        filtered_bars = UniverseFilter.from_config(dataset_config["universe"]).apply(bars)
        return DatasetPack(
            dataset_name=str(timeline_config["dataset"]["dataset_name"]),
            config=dataset_config,
            bars=filtered_bars,
            index_bars=load_daily_bars_from_csv(Path(dataset_config["paths"]["index_bars_csv"])),
            sector_snapshots=load_sector_snapshots_from_csv(Path(dataset_config["paths"]["sector_snapshots_csv"])),
            stock_snapshots=load_stock_snapshots_from_csv(Path(dataset_config["paths"]["stock_snapshots_csv"])),
            mainline_windows=load_mainline_windows_from_csv(Path(dataset_config["paths"]["mainline_windows_csv"])),
        )

    def _resolve_candidate(
        self,
        base_candidates: dict[str, dict[str, Any]],
        spec: dict[str, Any],
    ) -> RuleCandidate:
        from_base = str(spec.get("from_base") or spec["candidate_name"])
        base = base_candidates[from_base]
        merged_override = merge_config(dict(base.get("override", {})), dict(spec.get("override", {})))
        return RuleCandidate(
            candidate_name=str(spec["candidate_name"]),
            description=str(spec.get("description") or base.get("description") or ""),
            override=merged_override,
        )

    def _candidate_row(
        self,
        *,
        candidate_name: str,
        daily: dict[str, dict[str, Any]],
        control_daily: dict[str, dict[str, Any]],
        trigger_dates: list[str],
        total_pnl: float,
        trade_count: int,
        fill_count: int,
    ) -> dict[str, Any]:
        permission_repairs = 0
        assignment_repairs = 0
        combined_repairs = 0
        emitted_buy_repairs = 0

        for trigger_date in trigger_dates:
            row = daily.get(trigger_date, {})
            control_row = control_daily.get(trigger_date, {})
            candidate_permission = bool(row.get("permission_allowed"))
            control_permission = bool(control_row.get("permission_allowed"))
            candidate_assignment = str(row.get("assignment_layer") or "")
            control_assignment = str(control_row.get("assignment_layer") or "")
            candidate_actions = list(row.get("emitted_actions") or [])
            control_actions = list(control_row.get("emitted_actions") or [])

            permission_repaired = (not control_permission) and candidate_permission
            assignment_repaired = control_assignment == "junk" and candidate_assignment != "junk"
            buy_repaired = ("buy" not in control_actions) and ("buy" in candidate_actions)

            permission_repairs += int(permission_repaired)
            assignment_repairs += int(assignment_repaired)
            emitted_buy_repairs += int(buy_repaired)
            combined_repairs += int(permission_repaired or assignment_repaired or buy_repaired)

        repair_profile = "no_trigger_repairs"
        if combined_repairs > 0:
            if permission_repairs >= assignment_repairs and permission_repairs >= emitted_buy_repairs:
                repair_profile = "permission_led"
            elif assignment_repairs >= emitted_buy_repairs:
                repair_profile = "assignment_led"
            else:
                repair_profile = "entry_led"

        return {
            "candidate_name": candidate_name,
            "combined_repairs": combined_repairs,
            "permission_repairs": permission_repairs,
            "assignment_repairs": assignment_repairs,
            "emitted_buy_repairs": emitted_buy_repairs,
            "trade_count": trade_count,
            "fill_count": fill_count,
            "total_pnl": total_pnl,
            "repair_profile": repair_profile,
        }


def write_feature_pack_b_hierarchy_approval_sweep_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackBHierarchyApprovalSweepReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
