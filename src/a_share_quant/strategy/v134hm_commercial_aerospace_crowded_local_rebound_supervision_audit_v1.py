from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1 import (
    TARGET_SYMBOLS,
    V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


class V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_basic_path = (
            repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        )
        self.moneyflow_path = (
            repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_crowded_local_rebound_supervision_v1.csv"
        )

    def analyze(self) -> V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Report:
        named_audit = (
            V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer(self.repo_root).analyze()
        )
        with self.daily_basic_path.open("r", encoding="utf-8-sig", newline="") as handle:
            basic_rows = list(csv.DictReader(handle))
        with self.moneyflow_path.open("r", encoding="utf-8-sig", newline="") as handle:
            moneyflow_rows = list(csv.DictReader(handle))

        basic_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in basic_rows:
            symbol = row["symbol"]
            if symbol in TARGET_SYMBOLS and "20260115" <= row["trade_date"] <= "20260403":
                basic_by_symbol.setdefault(symbol, []).append(row)
        mf_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in moneyflow_rows:
            symbol = row["symbol"]
            if symbol in TARGET_SYMBOLS and "20260115" <= row["trade_date"] <= "20260403":
                mf_by_symbol.setdefault(symbol, []).append(row)

        symbol_rows: list[dict[str, Any]] = []
        family_counts: dict[str, int] = {}

        for base_row in named_audit.symbol_rows:
            symbol = base_row["symbol"]
            basic_symbol_rows = basic_by_symbol.get(symbol, [])
            mf_symbol_rows = mf_by_symbol.get(symbol, [])

            turnover_values = [
                float(row["turnover_rate_f"])
                for row in basic_symbol_rows
                if row.get("turnover_rate_f") not in {"", None}
            ]
            volume_ratio_values = [
                float(row["volume_ratio"])
                for row in basic_symbol_rows
                if row.get("volume_ratio") not in {"", None}
            ]
            net_mf_values = [
                float(row["net_mf_amount"])
                for row in mf_symbol_rows
                if row.get("net_mf_amount") not in {"", None}
            ]

            avg_turnover = round(sum(turnover_values) / len(turnover_values), 8) if turnover_values else ""
            max_turnover = round(max(turnover_values), 8) if turnover_values else ""
            avg_volume_ratio = round(sum(volume_ratio_values) / len(volume_ratio_values), 8) if volume_ratio_values else ""
            max_volume_ratio = round(max(volume_ratio_values), 8) if volume_ratio_values else ""
            total_net_mf = round(sum(net_mf_values), 2) if net_mf_values else ""

            peak_gap = base_row["post_lockout_max_vs_pre_lockout_peak"]
            peak_gap_float = float(peak_gap) if peak_gap != "" else None
            max_zone = base_row["max_date_zone"]

            if (
                peak_gap_float is not None
                and peak_gap_float > -0.06
                and max_zone == "post_lockout_raw_only_window"
                and turnover_values
                and max(turnover_values) >= 40.0
                and (sum(turnover_values) / len(turnover_values)) >= 20.0
            ):
                crowded_family = "crowding_like_shelter_rebound"
                reading = (
                    "near-high or breakout raw-only recovery with high turnover concentration fits crowding-like shelter rebound rather than board restart"
                )
            elif (
                peak_gap_float is not None
                and peak_gap_float > -0.03
                and max_zone == "post_lockout_raw_only_window"
            ):
                crowded_family = "high_beta_raw_only_rebound"
                reading = (
                    "strong raw-only rebound approaches prior peak but lacks the turnover-concentration signature of crowded shelter names"
                )
            elif base_row["counterexample_family"] == "lockout_outlier_breakout_then_fade":
                crowded_family = "lockout_outlier_breakout"
                reading = (
                    "breakout inside lockout still reads as local outlier strength under a closed board, not as legal board unlock"
                )
            elif base_row["counterexample_family"] == "locked_board_weak_repair_only":
                crowded_family = "locked_board_weak_repair"
                reading = (
                    "local repair remains too weak versus prior peak and does not justify renewed board participation"
                )
            else:
                crowded_family = "coverage_gap_or_unclassified"
                reading = "keep as auxiliary negative evidence until better local path coverage exists"

            symbol_row = {
                "symbol": symbol,
                "display_name": TARGET_SYMBOLS[symbol],
                "named_counterexample_family": base_row["counterexample_family"],
                "crowded_rebound_family": crowded_family,
                "post_lockout_max_vs_pre_lockout_peak": base_row["post_lockout_max_vs_pre_lockout_peak"],
                "max_date_zone": max_zone,
                "avg_turnover_rate_f": avg_turnover,
                "max_turnover_rate_f": max_turnover,
                "avg_volume_ratio": avg_volume_ratio,
                "max_volume_ratio": max_volume_ratio,
                "net_mf_amount_total": total_net_mf,
                "learning_reading": reading,
            }
            symbol_rows.append(symbol_row)
            family_counts[crowded_family] = family_counts.get(crowded_family, 0) + 1

        family_rows = [
            {"crowded_rebound_family": family, "symbol_count": count}
            for family, count in sorted(family_counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        summary = {
            "acceptance_posture": "freeze_v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1",
            "analysis_symbol_count": len(symbol_rows),
            "crowding_like_shelter_rebound_count": sum(
                1 for row in symbol_rows if row["crowded_rebound_family"] == "crowding_like_shelter_rebound"
            ),
            "high_beta_raw_only_rebound_count": sum(
                1 for row in symbol_rows if row["crowded_rebound_family"] == "high_beta_raw_only_rebound"
            ),
            "lockout_outlier_breakout_count": sum(
                1 for row in symbol_rows if row["crowded_rebound_family"] == "lockout_outlier_breakout"
            ),
            "authoritative_output": "commercial_aerospace_crowded_local_rebound_supervision_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34HM asks whether named strong rebounds after lockout contain a crowding-like shelter subset rather than a board-wide restart signal.",
            "This treats high-turnover near-high raw-only recoveries as negative-label candidates: symbol strength can concentrate in a few liquid names even while board unlock remains absent.",
        ]
        return V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
