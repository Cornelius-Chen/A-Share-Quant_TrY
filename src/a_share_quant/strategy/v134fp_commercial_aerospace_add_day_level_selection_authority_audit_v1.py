from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Report:
    summary: dict[str, Any]
    day_rows: list[dict[str, Any]]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "day_rows": self.day_rows,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


class V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )
        self.output_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_day_level_selection_authority_days_v1.csv"
        )

    @staticmethod
    def _strong_candidate(row: dict[str, Any]) -> bool:
        return (
            row["unlock_worthy"] == "True"
            and row["high_role_symbol"] == "True"
            and row["predicted_label"] == "allowed_preheat_full_add"
            and row["close_loc_15m"] is not None
            and row["close_loc_15m"] >= 0.63
            and row["open_to_60m"] >= 0.015
            and row["burst_amount_share_15"] <= 0.4
        )

    def analyze(self) -> V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Report:
        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            context_rows = list(csv.DictReader(handle))

        for row in context_rows:
            row["open_to_60m"] = float(row["open_to_60m"])
            row["close_loc_15m"] = float(row["close_loc_15m"]) if row["close_loc_15m"] else None
            row["burst_amount_share_15"] = float(row["burst_amount_share_15"])

        strong_rows = [row for row in context_rows if self._strong_candidate(row)]
        strong_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in strong_rows:
            strong_by_date[row["trade_date"]].append(row)

        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            order_rows = list(csv.DictReader(handle))

        actual_add_by_date: dict[str, list[str]] = defaultdict(list)
        for row in order_rows:
            if row["action"] in {"open", "add"}:
                actual_add_by_date[row["execution_trade_date"]].append(row["symbol"])

        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        allowed_seed_by_symbol: dict[str, list[str]] = defaultdict(list)
        for row in registry_rows:
            if row["supervision_tier"] == "allowed_add_seed":
                allowed_seed_by_symbol[row["symbol"]].append(row["execution_trade_date"])
        for trade_dates in allowed_seed_by_symbol.values():
            trade_dates.sort()

        symbol_calendars: dict[str, list[str]] = defaultdict(list)
        for row in context_rows:
            symbol_calendars[row["symbol"]].append(row["trade_date"])
        for symbol, dates in symbol_calendars.items():
            symbol_calendars[symbol] = sorted(set(dates))

        family_counter: dict[str, int] = defaultdict(int)
        day_rows: list[dict[str, Any]] = []

        for trade_date in sorted(strong_by_date):
            candidate_rows = sorted(strong_by_date[trade_date], key=lambda row: row["symbol"])
            candidate_symbols = [row["symbol"] for row in candidate_rows]
            actual_symbols = actual_add_by_date.get(trade_date, [])
            overlap_symbols = sorted(set(candidate_symbols) & set(actual_symbols))
            displaced_symbols = sorted(set(candidate_symbols) - set(actual_symbols))

            if overlap_symbols and set(overlap_symbols) == set(candidate_symbols):
                authority_family = "aligned_selection_day"
                rationale = "all strong local candidates were actually selected on the same day"
            elif actual_symbols:
                authority_family = "displaced_selection_day"
                rationale = (
                    "strong local candidates existed, but the live add day selected different symbols; the blocker is cross-symbol day-level selection authority"
                )
            else:
                authority_family = "post_wave_echo_day"
                rationale = (
                    "strong local candidates appeared on a no-order day, so they behave like late echoes after the earlier add wave rather than fresh permission"
                )
            family_counter[authority_family] += 1

            latest_gap = None
            latest_prior_date = ""
            for symbol in candidate_symbols:
                prior_dates = [value for value in allowed_seed_by_symbol[symbol] if value < trade_date]
                if not prior_dates:
                    continue
                prior_date = prior_dates[-1]
                calendar = symbol_calendars[symbol]
                gap = calendar.index(trade_date) - calendar.index(prior_date)
                if latest_gap is None or gap > latest_gap:
                    latest_gap = gap
                    latest_prior_date = prior_date

            day_rows.append(
                {
                    "trade_date": trade_date,
                    "authority_family": authority_family,
                    "candidate_symbol_count": len(candidate_symbols),
                    "candidate_symbols": "|".join(candidate_symbols),
                    "actual_add_symbol_count": len(actual_symbols),
                    "actual_add_symbols": "|".join(actual_symbols),
                    "overlap_symbol_count": len(overlap_symbols),
                    "overlap_symbols": "|".join(overlap_symbols),
                    "displaced_candidate_count": len(displaced_symbols),
                    "displaced_candidate_symbols": "|".join(displaced_symbols),
                    "max_trading_day_gap_from_prior_allowed_seed": latest_gap,
                    "reference_prior_allowed_trade_date": latest_prior_date,
                    "rationale": rationale,
                }
            )

        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        if day_rows:
            with self.output_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(day_rows[0].keys()))
                writer.writeheader()
                writer.writerows(day_rows)

        family_rows = [
            {"authority_family": family, "day_count": count}
            for family, count in sorted(family_counter.items())
        ]

        summary = {
            "acceptance_posture": "freeze_v134fp_commercial_aerospace_add_day_level_selection_authority_audit_v1",
            "candidate_day_count": len(day_rows),
            "aligned_selection_day_count": family_counter["aligned_selection_day"],
            "displaced_selection_day_count": family_counter["displaced_selection_day"],
            "post_wave_echo_day_count": family_counter["post_wave_echo_day"],
            "candidate_day_rows_csv": str(self.output_csv_path.relative_to(self.repo_root)) if day_rows else "",
            "authoritative_rule": (
                "the current add portability blocker is day-level selection authority: strong local candidates split into aligned days, displaced selection days, and post-wave echo days"
            ),
        }
        interpretation = [
            "V1.34FP audits the strongest local add candidates at the day level rather than the session level.",
            "The goal is to explain why a real local add object still cannot become a portable module even after its local shape looks strong.",
        ]
        return V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Report(
            summary=summary,
            day_rows=day_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fp_commercial_aerospace_add_day_level_selection_authority_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
