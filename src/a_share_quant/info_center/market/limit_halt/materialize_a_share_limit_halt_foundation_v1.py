from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _round_price(value: float) -> float:
    return round(value + 1e-8, 2)


def _limit_ratio(board: str, is_st: bool) -> float:
    if is_st:
        return 0.05
    if board == "ChiNext":
        return 0.20
    return 0.10


@dataclass(slots=True)
class MaterializedAShareLimitHaltFoundationV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareLimitHaltFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "akshare_daily_bars_bootstrap.csv"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.surface_path = self.output_dir / "a_share_limit_halt_surface_v1.csv"
        self.residual_path = self.output_dir / "a_share_limit_halt_residual_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_limit_halt_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareLimitHaltFoundationV1:
        identity_rows = _read_csv(self.identity_path)
        daily_rows = _read_csv(self.daily_path)
        board_by_symbol = {row["symbol"]: row["board"] for row in identity_rows}

        rows: list[dict[str, Any]] = []
        for row in daily_rows:
            symbol = row["symbol"]
            board = board_by_symbol.get(symbol, "Unknown")
            pre_close = float(row["pre_close"] or 0.0)
            close = float(row["close"] or 0.0)
            high = float(row["high"] or 0.0)
            low = float(row["low"] or 0.0)
            is_st = str(row["is_st"]).lower() == "true"
            is_suspended = str(row["is_suspended"]).lower() == "true"
            limit_ratio = _limit_ratio(board, is_st)

            if pre_close > 0:
                upper_limit = _round_price(pre_close * (1.0 + limit_ratio))
                lower_limit = _round_price(pre_close * (1.0 - limit_ratio))
            else:
                upper_limit = 0.0
                lower_limit = 0.0

            limit_up_hit = upper_limit > 0 and high >= upper_limit and close >= upper_limit
            limit_down_hit = lower_limit > 0 and low <= lower_limit and close <= lower_limit

            rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": symbol,
                    "board": board,
                    "is_st": is_st,
                    "is_suspended": is_suspended,
                    "limit_ratio": limit_ratio,
                    "upper_limit_price": f"{upper_limit:.2f}",
                    "lower_limit_price": f"{lower_limit:.2f}",
                    "limit_up_hit": limit_up_hit,
                    "limit_down_hit": limit_down_hit,
                    "halt_or_suspend_flag": is_suspended,
                }
            )

        residual_rows = [
            {
                "residual_class": "exchange_rule_precision_gap",
                "residual_reason": "bootstrap limit surface uses board heuristics and does not yet model special exchange rule exceptions",
            },
            {
                "residual_class": "intraday_limit_state_gap",
                "residual_reason": "current surface is daily close-based and does not yet provide minute-level open-close board lock information",
            },
            {
                "residual_class": "star_beijing_coverage_gap",
                "residual_reason": "current identity surface contains Main and ChiNext only; no STAR or BSE-specific limit regime is active in bootstrap coverage",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, data_rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(data_rows[0].keys()))
                writer.writeheader()
                writer.writerows(data_rows)

        _write(self.surface_path, rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "surface_row_count": len(rows),
            "limit_up_hit_count": sum(str(row["limit_up_hit"]) == "True" for row in rows),
            "limit_down_hit_count": sum(str(row["limit_down_hit"]) == "True" for row in rows),
            "halt_or_suspend_count": sum(str(row["halt_or_suspend_flag"]) == "True" for row in rows),
            "residual_count": len(residual_rows),
            "surface_path": str(self.surface_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareLimitHaltFoundationV1(
            summary=summary, rows=rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareLimitHaltFoundationV1(repo_root).materialize()
    print(result.summary["surface_path"])


if __name__ == "__main__":
    main()
