from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)
from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _ReplayConfig,
    _load_csv,
)
from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    _VetoPolicy,
)


@dataclass(slots=True)
class V127OCommercialAerospaceNewPrimaryAttributionReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    symbol_attribution_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "symbol_attribution_rows": self.symbol_attribution_rows,
            "interpretation": self.interpretation,
        }


class V127OCommercialAerospaceNewPrimaryAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.v127m_path = repo_root / "reports" / "analysis" / "v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1.json"

    @staticmethod
    def _blocked(row: dict[str, Any], policy: _VetoPolicy) -> bool:
        symbol = row["symbol"]
        phase = row["phase_window_semantic"]
        if symbol in policy.global_symbols:
            return True
        if phase == "preheat_window" and symbol in policy.preheat_symbols:
            return True
        if phase == "impulse_window" and symbol in policy.impulse_symbols:
            return True
        return False

    def _drag_symbols(self) -> list[str]:
        payload = json.loads(self.v127m_path.read_text(encoding="utf-8"))
        return payload["summary"]["drag_symbols_ranked"]

    def _simulate_with_policy(self, policy: _VetoPolicy) -> dict[str, Any]:
        base = self.helper._load_base_config()
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self.helper._split_rows(label_table.training_rows)
        filtered_rows = [row for row in rows if not self._blocked(row, policy)]
        config = _ReplayConfig(
            name=policy.name,
            preheat_cap=int(base["preheat_cap"]),
            impulse_cap=int(base["impulse_cap"]),
            cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
            min_increment_notional=float(base["min_increment_notional"]),
            preheat_full_target_notional=70_000.0,
            family="broad_half_reference",
            sell_ratio=0.5,
        )
        return self.helper._simulate_variant_detailed(filtered_rows, test_dates, date_to_idx, config)

    def analyze(self) -> V127OCommercialAerospaceNewPrimaryAttributionReport:
        drag_symbols = self._drag_symbols()
        old_primary = self._simulate_with_policy(
            _VetoPolicy("broad_half_reference", set(), set(), set())
        )
        new_primary = self._simulate_with_policy(
            _VetoPolicy("veto_drag_trio_impulse_only", set(), set(), set(drag_symbols[:3]))
        )
        daily_map = {
            (row["symbol"], row["trade_date"]): row
            for row in _load_csv(self.daily_path)
        }
        variants = [old_primary, new_primary]
        variant_rows: list[dict[str, Any]] = []
        symbol_attribution_rows: list[dict[str, Any]] = []
        for variant in variants:
            summary = variant["summary"]
            order_rows = variant["order_rows"]
            daily_rows = variant["daily_rows"]
            variant_rows.append(
                {
                    "variant": variant["variant"],
                    "final_equity": round(float(summary["final_equity"]), 4),
                    "max_drawdown": round(float(summary["max_drawdown"]), 8),
                    "executed_order_count": int(summary["executed_order_count"]),
                    "open_order_count": sum(1 for row in order_rows if row["action"] == "open"),
                    "reduce_order_count": sum(1 for row in order_rows if row["action"] == "reduce"),
                }
            )
            symbol_attribution_rows.extend(
                self.helper._symbol_attribution_rows(
                    variant_name=variant["variant"],
                    daily_rows=daily_rows,
                    order_rows=order_rows,
                    daily_map=daily_map,
                )
            )
        summary = {
            "acceptance_posture": "freeze_v127o_commercial_aerospace_new_primary_attribution_v1",
            "old_primary_variant": old_primary["variant"],
            "old_primary_final_equity": old_primary["summary"]["final_equity"],
            "old_primary_max_drawdown": old_primary["summary"]["max_drawdown"],
            "new_primary_variant": new_primary["variant"],
            "new_primary_final_equity": new_primary["summary"]["final_equity"],
            "new_primary_max_drawdown": new_primary["summary"]["max_drawdown"],
            "equity_delta": round(
                float(new_primary["summary"]["final_equity"]) - float(old_primary["summary"]["final_equity"]),
                4,
            ),
            "drawdown_delta": round(
                float(new_primary["summary"]["max_drawdown"]) - float(old_primary["summary"]["max_drawdown"]),
                8,
            ),
        }
        interpretation = [
            "V1.27O explains why the new primary reference beats the old broad-half reference after selective impulse-phase drag veto.",
            "The purpose is to identify which symbols actually improved and whether the gain came from cleaner entry selection rather than more selling.",
        ]
        return V127OCommercialAerospaceNewPrimaryAttributionReport(
            summary=summary,
            variant_rows=variant_rows,
            symbol_attribution_rows=symbol_attribution_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127OCommercialAerospaceNewPrimaryAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127OCommercialAerospaceNewPrimaryAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127o_commercial_aerospace_new_primary_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
