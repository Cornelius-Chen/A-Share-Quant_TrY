from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from a_share_quant.strategy.v134ev_commercial_aerospace_broader_add_false_positive_audit_v1 import (
    _predict_broader_add_label,
    _safe_close_location,
    _symbol_to_archive_member,
)


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


@dataclass(slots=True)
class V134EZCommercialAerospaceAddPermissionContextAuditV1Report:
    summary: dict[str, Any]
    feature_rows: list[dict[str, Any]]
    scenario_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_rows": self.feature_rows,
            "scenario_rows": self.scenario_rows,
            "interpretation": self.interpretation,
        }


class V134EZCommercialAerospaceAddPermissionContextAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.context_gating_report_path = (
            repo_root / "reports" / "analysis" / "v134ex_commercial_aerospace_add_context_gating_audit_v1.json"
        )
        self.expectancy_audit_path = (
            repo_root / "reports" / "analysis" / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )

    def analyze(self) -> V134EZCommercialAerospaceAddPermissionContextAuditV1Report:
        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        seed_map = {(row["execution_trade_date"], row["symbol"]): row for row in registry_rows}
        seed_symbols = sorted({row["symbol"] for row in registry_rows})
        full_capable_symbols = {
            symbol for symbol, count in self._full_capable_symbol_counts(registry_rows).items() if count >= 2
        }

        expectancy = json.loads(self.expectancy_audit_path.read_text(encoding="utf-8"))
        unlock_dates = {
            row["trade_date"] for row in expectancy["seed_rows"] if row["expectancy_state"] == "unlock_worthy"
        }
        slow_context = json.loads(self.context_gating_report_path.read_text(encoding="utf-8"))
        slow_best_ratio = slow_context["summary"]["best_scenario_non_seed_to_seed_ratio"]

        session_rows: list[dict[str, Any]] = []

        for month_dir in sorted(self.monthly_root.iterdir()):
            if not month_dir.is_dir():
                continue
            for zip_path in sorted(month_dir.glob("*_1min.zip")):
                trade_date = zip_path.stem.replace("_1min", "")
                with zipfile.ZipFile(zip_path) as archive:
                    names = set(archive.namelist())
                    for symbol in seed_symbols:
                        member_name = _symbol_to_archive_member(symbol)
                        if member_name not in names:
                            continue
                        with archive.open(member_name, "r") as member:
                            minute_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:61]
                        if len(minute_rows) < 60:
                            continue

                        first_60 = minute_rows[:60]
                        opens = [float(row[3]) for row in first_60]
                        closes = [float(row[4]) for row in first_60]
                        highs = [float(row[5]) for row in first_60]
                        lows = [float(row[6]) for row in first_60]
                        amounts = [float(row[8]) for row in first_60]
                        base_open = opens[0]

                        open_to_5m = closes[4] / base_open - 1.0
                        open_to_15m = closes[14] / base_open - 1.0
                        open_to_60m = closes[59] / base_open - 1.0
                        close_loc_15m = _safe_close_location(max(highs[:15]), min(lows[:15]), closes[14])
                        board_lockout_active = int(trade_date) >= 20260115
                        predicted_label = _predict_broader_add_label(
                            board_lockout_active=board_lockout_active,
                            open_to_5m=open_to_5m,
                            open_to_15m=open_to_15m,
                            open_to_60m=open_to_60m,
                            close_loc_15m=close_loc_15m,
                        )
                        if predicted_label not in {"allowed_preheat_probe_add", "allowed_preheat_full_add"}:
                            continue

                        amount_15 = sum(amounts[:15])
                        amount_60 = sum(amounts)
                        up_amount_15 = sum(
                            amount for amount, open_px, close_px in zip(amounts[:15], opens[:15], closes[:15]) if close_px > open_px
                        )
                        down_amount_15 = sum(
                            amount for amount, open_px, close_px in zip(amounts[:15], opens[:15], closes[:15]) if close_px < open_px
                        )
                        pos_minute_count_15 = sum(1 for open_px, close_px in zip(opens[:15], closes[:15]) if close_px > open_px)
                        neg_minute_count_15 = sum(1 for open_px, close_px in zip(opens[:15], closes[:15]) if close_px < open_px)

                        seed_row = seed_map.get((trade_date, symbol))
                        is_seed_allowed = bool(seed_row and seed_row["supervision_tier"] == "allowed_add_seed")

                        session_rows.append(
                            {
                                "trade_date": trade_date,
                                "month_bucket": f"{trade_date[:4]}-{trade_date[4:6]}",
                                "symbol": symbol,
                                "predicted_label": predicted_label,
                                "is_seed_allowed": is_seed_allowed,
                                "unlock_worthy": trade_date in unlock_dates,
                                "high_role_symbol": symbol in full_capable_symbols,
                                "open_to_5m": round(open_to_5m, 8),
                                "open_to_15m": round(open_to_15m, 8),
                                "open_to_60m": round(open_to_60m, 8),
                                "close_loc_15m": round(close_loc_15m, 8) if close_loc_15m is not None else None,
                                "burst_amount_share_15": round(_safe_divide(amount_15, amount_60), 8),
                                "up_amount_share_15": round(_safe_divide(up_amount_15, amount_15), 8),
                                "down_amount_share_15": round(_safe_divide(down_amount_15, amount_15), 8),
                                "pos_minute_count_15": pos_minute_count_15,
                                "neg_minute_count_15": neg_minute_count_15,
                                "max_return_15m": round(max(high / base_open - 1.0 for high in highs[:15]), 8),
                            }
                        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        seed_rows = [row for row in session_rows if row["is_seed_allowed"]]
        non_seed_rows = [row for row in session_rows if not row["is_seed_allowed"]]
        feature_rows = self._build_feature_rows(seed_rows, non_seed_rows)

        scenarios: list[tuple[str, Callable[[dict[str, Any]], bool], str]] = [
            ("baseline_positive_shape", lambda row: True, "ungated positive shape-only add hits on the broader local first-hour surface"),
            ("slow_unlock_high_role", lambda row: row["unlock_worthy"] and row["high_role_symbol"], "the best available slow-context gate from V1.34EX"),
            ("contained_burst15_only", lambda row: row["burst_amount_share_15"] <= 0.40, "filter out opening sessions that consume too much of the hour's amount too early"),
            (
                "contained_close15_plus_burst15",
                lambda row: row["close_loc_15m"] is not None and row["close_loc_15m"] <= 0.58 and row["burst_amount_share_15"] <= 0.40,
                "keep positive add only when the early path is constructive but not overly pinned to the first-15m high",
            ),
            (
                "contained_close15_plus_burst15_plus_posmin15",
                lambda row: row["close_loc_15m"] is not None
                and row["close_loc_15m"] <= 0.58
                and row["burst_amount_share_15"] <= 0.40
                and row["pos_minute_count_15"] <= 6,
                "point-in-time moderation: early path can be positive, but it cannot already look like a crowded opening chase",
            ),
            (
                "slow_unlock_high_role_plus_contained_burst15",
                lambda row: row["unlock_worthy"] and row["high_role_symbol"] and row["burst_amount_share_15"] <= 0.40,
                "narrow high-confidence permission clue that combines the best slow-context gate with early amount containment",
            ),
        ]

        scenario_rows: list[dict[str, Any]] = []
        for scenario_name, predicate, reading in scenarios:
            kept_rows = [row for row in session_rows if predicate(row)]
            seed_kept = sum(1 for row in kept_rows if row["is_seed_allowed"])
            non_seed_kept = len(kept_rows) - seed_kept
            scenario_rows.append(
                {
                    "scenario_name": scenario_name,
                    "kept_positive_hit_count": len(kept_rows),
                    "seed_kept_count": seed_kept,
                    "non_seed_kept_count": non_seed_kept,
                    "non_seed_to_seed_ratio": round(non_seed_kept / seed_kept, 8) if seed_kept else 0.0,
                    "reading": reading,
                }
            )

        best_broad_pt = next(row for row in scenario_rows if row["scenario_name"] == "contained_close15_plus_burst15_plus_posmin15")
        best_high_conf = next(row for row in scenario_rows if row["scenario_name"] == "slow_unlock_high_role_plus_contained_burst15")

        summary = {
            "acceptance_posture": "freeze_v134ez_commercial_aerospace_add_permission_context_audit_v1",
            "positive_hit_session_count": len(session_rows),
            "seed_allowed_hit_count": len(seed_rows),
            "non_seed_positive_hit_count": len(non_seed_rows),
            "best_slow_context_ratio": slow_best_ratio,
            "best_point_in_time_broad_scenario": best_broad_pt["scenario_name"],
            "best_point_in_time_broad_ratio": best_broad_pt["non_seed_to_seed_ratio"],
            "best_point_in_time_broad_seed_kept_count": best_broad_pt["seed_kept_count"],
            "best_point_in_time_broad_non_seed_kept_count": best_broad_pt["non_seed_kept_count"],
            "best_high_confidence_scenario": best_high_conf["scenario_name"],
            "best_high_confidence_ratio": best_high_conf["non_seed_to_seed_ratio"],
            "best_high_confidence_seed_kept_count": best_high_conf["seed_kept_count"],
            "best_high_confidence_non_seed_kept_count": best_high_conf["non_seed_kept_count"],
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "point-in-time quantity-price moderation improves positive add density more than slow context alone, "
                "but it still does not justify broader positive add promotion; the best current use is a narrow high-confidence supervision clue"
            ),
        }
        interpretation = [
            "V1.34EZ adds a true point-in-time quantity-price permission audit on the broader positive add surface.",
            "The key result is that early moderation helps more than slow context alone: authentic add seeds look less chasey than the broader shape-only positive population.",
            "Even so, the branch still does not support broad positive add expansion; the strongest new result is a narrow high-confidence permission clue, not a replay-facing permission rule.",
        ]
        return V134EZCommercialAerospaceAddPermissionContextAuditV1Report(
            summary=summary,
            feature_rows=feature_rows,
            scenario_rows=scenario_rows,
            interpretation=interpretation,
        )

    @staticmethod
    def _full_capable_symbol_counts(rows: list[dict[str, str]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            if row["seed_family"] != "preheat_full_add":
                continue
            if row["supervision_tier"] != "allowed_add_seed":
                continue
            counts[row["symbol"]] = counts.get(row["symbol"], 0) + 1
        return counts

    @staticmethod
    def _build_feature_rows(seed_rows: list[dict[str, Any]], non_seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        feature_names = [
            "open_to_5m",
            "open_to_15m",
            "close_loc_15m",
            "burst_amount_share_15",
            "up_amount_share_15",
            "down_amount_share_15",
            "pos_minute_count_15",
            "neg_minute_count_15",
            "max_return_15m",
        ]
        output: list[dict[str, Any]] = []
        for feature_name in feature_names:
            seed_values = [float(row[feature_name]) for row in seed_rows if row[feature_name] is not None]
            non_seed_values = [float(row[feature_name]) for row in non_seed_rows if row[feature_name] is not None]
            seed_mean = sum(seed_values) / len(seed_values) if seed_values else 0.0
            non_seed_mean = sum(non_seed_values) / len(non_seed_values) if non_seed_values else 0.0
            output.append(
                {
                    "feature_name": feature_name,
                    "seed_allowed_mean": round(seed_mean, 8),
                    "non_seed_positive_mean": round(non_seed_mean, 8),
                    "mean_gap_seed_minus_non_seed": round(seed_mean - non_seed_mean, 8),
                }
            )
        return output


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EZCommercialAerospaceAddPermissionContextAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EZCommercialAerospaceAddPermissionContextAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ez_commercial_aerospace_add_permission_context_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
