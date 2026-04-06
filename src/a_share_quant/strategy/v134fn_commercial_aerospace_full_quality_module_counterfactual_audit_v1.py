from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Report:
    summary: dict[str, Any]
    counterfactual_rows: list[dict[str, Any]]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "counterfactual_rows": self.counterfactual_rows,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


class V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.output_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_full_quality_module_counterfactual_sessions_v1.csv"
        )

    @staticmethod
    def _best_scenario_match(row: dict[str, Any]) -> bool:
        return (
            row["unlock_worthy"] == "True"
            and row["high_role_symbol"] == "True"
            and row["predicted_label"] == "allowed_preheat_full_add"
            and row["close_loc_15m"] is not None
            and row["close_loc_15m"] >= 0.63
            and row["open_to_60m"] >= 0.015
            and row["burst_amount_share_15"] <= 0.4
        )

    def analyze(self) -> V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Report:
        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            context_rows = list(csv.DictReader(handle))

        for row in context_rows:
            row["open_to_15m"] = float(row["open_to_15m"])
            row["open_to_60m"] = float(row["open_to_60m"])
            row["close_loc_15m"] = float(row["close_loc_15m"]) if row["close_loc_15m"] else None
            row["burst_amount_share_15"] = float(row["burst_amount_share_15"])

        matched_rows = [row for row in context_rows if self._best_scenario_match(row)]

        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        allowed_seed_by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in registry_rows:
            if row["supervision_tier"] == "allowed_add_seed":
                allowed_seed_by_symbol[row["symbol"]].append(row)
        for rows in allowed_seed_by_symbol.values():
            rows.sort(key=lambda row: row["execution_trade_date"])

        symbol_calendars: dict[str, list[str]] = defaultdict(list)
        for row in context_rows:
            symbol_calendars[row["symbol"]].append(row["trade_date"])
        for symbol, trade_dates in symbol_calendars.items():
            symbol_calendars[symbol] = sorted(set(trade_dates))

        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            order_rows = list(csv.DictReader(handle))

        same_day_open_add_symbols: dict[str, list[str]] = defaultdict(list)
        for row in order_rows:
            if row["action"] in {"open", "add"}:
                same_day_open_add_symbols[row["execution_trade_date"]].append(row["symbol"])

        counterfactual_rows: list[dict[str, Any]] = []
        family_counter: dict[str, int] = defaultdict(int)
        trading_day_gaps: list[int] = []

        for row in matched_rows:
            if row["is_seed_allowed"] == "True":
                continue

            symbol = row["symbol"]
            trade_date = row["trade_date"]
            prior_allowed_rows = [
                seed_row for seed_row in allowed_seed_by_symbol[symbol] if seed_row["execution_trade_date"] < trade_date
            ]
            prior_allowed_row = prior_allowed_rows[-1] if prior_allowed_rows else None
            prior_allowed_trade_date = prior_allowed_row["execution_trade_date"] if prior_allowed_row else ""
            prior_allowed_family = prior_allowed_row["seed_family"] if prior_allowed_row else ""

            trading_day_gap = None
            if prior_allowed_trade_date:
                calendar = symbol_calendars[symbol]
                trading_day_gap = calendar.index(trade_date) - calendar.index(prior_allowed_trade_date)
                trading_day_gaps.append(trading_day_gap)

            same_day_symbols = same_day_open_add_symbols.get(trade_date, [])
            if same_day_symbols:
                counterfactual_family = "selection_displacement_counterfactual"
                rationale = (
                    "a real open/add day already existed, so this candidate behaves like a displaced alternative rather than a portable add permission"
                )
            else:
                counterfactual_family = "no_order_day_post_seed_echo"
                rationale = (
                    "the local add shape appears on a no-order day after the symbol's earlier allowed-add phase, so it behaves like a late echo rather than fresh permission"
                )
            family_counter[counterfactual_family] += 1

            counterfactual_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "counterfactual_family": counterfactual_family,
                    "prior_allowed_trade_date": prior_allowed_trade_date,
                    "prior_allowed_family": prior_allowed_family,
                    "trading_days_since_prior_allowed_seed": trading_day_gap,
                    "same_day_actual_open_add_symbols": "|".join(same_day_symbols),
                    "open_to_15m": round(row["open_to_15m"], 8),
                    "open_to_60m": round(row["open_to_60m"], 8),
                    "close_loc_15m": round(row["close_loc_15m"], 8) if row["close_loc_15m"] is not None else None,
                    "burst_amount_share_15": round(row["burst_amount_share_15"], 8),
                    "rationale": rationale,
                }
            )

        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        if counterfactual_rows:
            with self.output_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(counterfactual_rows[0].keys()))
                writer.writeheader()
                writer.writerows(counterfactual_rows)

        family_rows = [
            {"counterfactual_family": family, "session_count": count}
            for family, count in sorted(family_counter.items())
        ]

        seed_match_count = sum(1 for row in matched_rows if row["is_seed_allowed"] == "True")
        summary = {
            "acceptance_posture": "freeze_v134fn_commercial_aerospace_full_quality_module_counterfactual_audit_v1",
            "scenario_name": "unlock_high_role_full_archetype_with_burst",
            "matched_session_count": len(matched_rows),
            "seed_match_count": seed_match_count,
            "counterfactual_count": len(counterfactual_rows),
            "counterfactual_symbol_count": len({row["symbol"] for row in counterfactual_rows}),
            "post_seed_echo_count": sum(1 for row in counterfactual_rows if row["prior_allowed_trade_date"]),
            "selection_displacement_counterfactual_count": family_counter["selection_displacement_counterfactual"],
            "no_order_day_post_seed_echo_count": family_counter["no_order_day_post_seed_echo"],
            "mean_trading_days_since_prior_allowed_seed": round(sum(trading_day_gaps) / len(trading_day_gaps), 8)
            if trading_day_gaps
            else 0.0,
            "counterfactual_rows_csv": str(self.output_csv_path.relative_to(self.repo_root)) if counterfactual_rows else "",
            "authoritative_rule": (
                "the residual non-seed hits are not random shape noise; they are displaced or late-echo counterfactuals that still require day-level selection authority"
            ),
        }
        interpretation = [
            "V1.34FN explains why the strongest portable-looking add scenario still cannot be promoted even after its local archetype became very clean.",
            "The remaining non-seed hits cluster into displaced same-day alternatives and late same-symbol echoes after earlier allowed-add phases, which means the blocker has shifted from local shape to day-level selection authority.",
        ]
        return V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Report(
            summary=summary,
            counterfactual_rows=counterfactual_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fn_commercial_aerospace_full_quality_module_counterfactual_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
