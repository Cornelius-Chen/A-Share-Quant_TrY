from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


def _safe_close_location(high_value: float, low_value: float, close_value: float) -> float | None:
    span = high_value - low_value
    if span <= 0:
        return None
    return (close_value - low_value) / span


def _predict_broader_add_label(*, board_lockout_active: bool, open_to_5m: float, open_to_15m: float, open_to_60m: float, close_loc_15m: float | None) -> str:
    if (
        board_lockout_active
        and close_loc_15m is not None
        and close_loc_15m >= 0.4
        and open_to_15m > -0.01
        and open_to_60m < 0.0
    ):
        return "blocked_board_lockout_add"
    if (
        not board_lockout_active
        and close_loc_15m is not None
        and open_to_5m <= -0.05
        and close_loc_15m <= 0.05
    ):
        return "failed_impulse_chase_add"
    if (
        not board_lockout_active
        and close_loc_15m is not None
        and open_to_15m > 0.005
        and close_loc_15m >= 0.6
    ):
        return "allowed_preheat_full_add"
    if not board_lockout_active and open_to_15m > -0.015:
        return "allowed_preheat_probe_add"
    return "unmatched_add_session"


@dataclass(slots=True)
class V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Report:
    summary: dict[str, Any]
    hit_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "hit_rows": self.hit_rows,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_broader_add_false_positive_hits_v1.csv"
        )

    @staticmethod
    def _target_label(row: dict[str, str]) -> str:
        if row["supervision_tier"] == "blocked_add_seed":
            return "blocked_board_lockout_add"
        if row["supervision_tier"] == "failed_add_seed":
            return "failed_impulse_chase_add"
        if row["seed_family"] == "preheat_full_add":
            return "allowed_preheat_full_add"
        return "allowed_preheat_probe_add"

    def analyze(self) -> V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Report:
        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        seed_map = {
            (row["execution_trade_date"], row["symbol"]): row for row in registry_rows
        }
        seed_symbols = sorted({row["symbol"] for row in registry_rows})

        hit_rows: list[dict[str, Any]] = []
        symbol_session_counts = {symbol: 0 for symbol in seed_symbols}
        symbol_positive_hit_counts = {symbol: 0 for symbol in seed_symbols}
        total_session_count = 0
        seed_session_count = 0
        seed_match_count = 0

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
                            minute_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
                        if len(minute_rows) < 60:
                            continue
                        total_session_count += 1
                        symbol_session_counts[symbol] += 1

                        first_60 = minute_rows[:60]
                        base_open = float(first_60[0][3])
                        close_5 = float(first_60[4][4])
                        close_15 = float(first_60[14][4])
                        close_60 = float(first_60[59][4])
                        high_15 = max(float(row[5]) for row in first_60[:15])
                        low_15 = min(float(row[6]) for row in first_60[:15])

                        open_to_5m = close_5 / base_open - 1.0
                        open_to_15m = close_15 / base_open - 1.0
                        open_to_60m = close_60 / base_open - 1.0
                        close_loc_15m = _safe_close_location(high_15, low_15, close_15)
                        board_lockout_active = int(trade_date) >= 20260115

                        predicted_label = _predict_broader_add_label(
                            board_lockout_active=board_lockout_active,
                            open_to_5m=open_to_5m,
                            open_to_15m=open_to_15m,
                            open_to_60m=open_to_60m,
                            close_loc_15m=close_loc_15m,
                        )

                        seed_row = seed_map.get((trade_date, symbol))
                        target_label = self._target_label(seed_row) if seed_row is not None else "none"
                        if seed_row is not None:
                            seed_session_count += 1
                            if predicted_label == target_label:
                                seed_match_count += 1

                        is_positive_candidate = predicted_label in {
                            "allowed_preheat_probe_add",
                            "allowed_preheat_full_add",
                        }
                        if is_positive_candidate:
                            symbol_positive_hit_counts[symbol] += 1

                        if predicted_label == "unmatched_add_session":
                            continue

                        hit_rows.append(
                            {
                                "trade_date": trade_date,
                                "month_bucket": f"{trade_date[:4]}-{trade_date[4:6]}",
                                "symbol": symbol,
                                "is_seed_session": seed_row is not None,
                                "target_label": target_label,
                                "predicted_label": predicted_label,
                                "board_lockout_active": board_lockout_active,
                                "open_to_5m": round(open_to_5m, 8),
                                "open_to_15m": round(open_to_15m, 8),
                                "open_to_60m": round(open_to_60m, 8),
                                "close_loc_15m": round(close_loc_15m, 8) if close_loc_15m is not None else None,
                            }
                        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if hit_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(hit_rows[0].keys()))
                writer.writeheader()
                writer.writerows(hit_rows)

        non_seed_hits = [row for row in hit_rows if not row["is_seed_session"]]
        non_seed_positive_hits = [
            row for row in non_seed_hits if row["predicted_label"] in {"allowed_preheat_probe_add", "allowed_preheat_full_add"}
        ]
        non_seed_failed_hits = [row for row in non_seed_hits if row["predicted_label"] == "failed_impulse_chase_add"]
        non_seed_blocked_hits = [row for row in non_seed_hits if row["predicted_label"] == "blocked_board_lockout_add"]

        symbol_rows = []
        for symbol in seed_symbols:
            session_count = symbol_session_counts[symbol]
            positive_hit_count = symbol_positive_hit_counts[symbol]
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "session_count": session_count,
                    "positive_hit_count": positive_hit_count,
                    "positive_hit_rate": round(positive_hit_count / session_count, 8) if session_count else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134ev_commercial_aerospace_broader_add_false_positive_audit_v1",
            "seed_symbol_count": len(seed_symbols),
            "total_session_count": total_session_count,
            "seed_session_count": seed_session_count,
            "seed_match_count": seed_match_count,
            "non_seed_positive_hit_count": len(non_seed_positive_hits),
            "non_seed_positive_hit_rate": round(len(non_seed_positive_hits) / (total_session_count - seed_session_count), 8)
            if total_session_count > seed_session_count
            else 0.0,
            "non_seed_failed_hit_count": len(non_seed_failed_hits),
            "non_seed_blocked_hit_count": len(non_seed_blocked_hits),
            "max_symbol_positive_hit_rate": max((row["positive_hit_rate"] for row in symbol_rows), default=0.0),
            "hit_rows_csv": str(self.output_csv.relative_to(self.repo_root)) if hit_rows else "",
            "authoritative_rule": (
                "the first local add rules do not yet support broader positive expansion if shape-only allowed-add hits become too dense on the wider local session surface"
            ),
        }
        interpretation = [
            "V1.34EV expands the first add rule candidates from the 55-row seed surface to all locally available first-hour sessions for the retained add symbols.",
            "The key governance question is whether shape-only positive add rules stay sparse enough outside the seed surface to justify broader expansion.",
        ]
        return V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Report(
            summary=summary,
            hit_rows=hit_rows,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ev_commercial_aerospace_broader_add_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
