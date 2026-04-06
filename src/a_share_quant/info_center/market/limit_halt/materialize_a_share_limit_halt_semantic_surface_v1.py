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


def _normalize_trade_date(value: str) -> str:
    value = str(value).strip()
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value


def _safe_float(value: Any) -> float:
    text = str(value).strip()
    if not text:
        return 0.0
    return float(text)


def _is_st_proxy(row: dict[str, str]) -> bool:
    name = str(row.get("name", "")).upper()
    reason = str(row.get("change_reason", "")).upper()
    return "ST" in name or "ST" in reason


@dataclass(slots=True)
class MaterializedAShareLimitHaltSemanticSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareLimitHaltSemanticSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        self.raw_daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"
        self.namechange_path = repo_root / "data" / "reference" / "namechange" / "tushare_commercial_aerospace_namechange_v1.csv"
        self.suspend_path = repo_root / "data" / "reference" / "suspend_d" / "tushare_commercial_aerospace_suspend_d_v1.csv"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.surface_path = self.output_dir / "a_share_limit_halt_semantic_surface_v1.csv"
        self.residual_path = self.output_dir / "a_share_limit_halt_semantic_surface_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_limit_halt_semantic_surface_manifest_v1.json"

    def materialize(self) -> MaterializedAShareLimitHaltSemanticSurfaceV1:
        identity_rows = _read_csv(self.identity_path)
        raw_daily_rows = _read_csv(self.raw_daily_path)
        stk_limit_rows = _read_csv(self.stk_limit_path)
        namechange_rows = _read_csv(self.namechange_path)
        suspend_rows = _read_csv(self.suspend_path)

        board_by_symbol = {row["symbol"]: row.get("board", "Unknown") for row in identity_rows}
        stk_limit_by_key = {
            (row["symbol"], _normalize_trade_date(row["trade_date"])): row for row in stk_limit_rows
        }
        suspend_keys = {
            (row["symbol"], _normalize_trade_date(row["trade_date"])) for row in suspend_rows
        }

        st_ranges_by_symbol: dict[str, list[tuple[str, str | None]]] = {}
        for row in namechange_rows:
            if not _is_st_proxy(row):
                continue
            symbol = row["symbol"]
            start_date = _normalize_trade_date(str(row.get("start_date", "")))
            end_date = _normalize_trade_date(str(row.get("end_date", ""))) or None
            if not start_date:
                continue
            st_ranges_by_symbol.setdefault(symbol, []).append((start_date, end_date))

        rows: list[dict[str, Any]] = []
        st_proxy_row_count = 0
        suspended_row_count = 0
        missing_stk_limit_count = 0
        for row in raw_daily_rows:
            symbol = row["symbol"]
            trade_date = _normalize_trade_date(row["trade_date"])
            board = board_by_symbol.get(symbol, "Unknown")
            pre_close = _safe_float(row.get("pre_close"))
            close = _safe_float(row.get("close"))
            high = _safe_float(row.get("high"))
            low = _safe_float(row.get("low"))

            is_st = False
            for start_date, end_date in st_ranges_by_symbol.get(symbol, []):
                if trade_date >= start_date and (end_date is None or trade_date <= end_date):
                    is_st = True
                    break
            if is_st:
                st_proxy_row_count += 1

            is_suspended = (symbol, trade_date) in suspend_keys
            if is_suspended:
                suspended_row_count += 1

            stk_limit_row = stk_limit_by_key.get((symbol, trade_date))
            if stk_limit_row:
                upper_limit = _safe_float(stk_limit_row.get("up_limit"))
                lower_limit = _safe_float(stk_limit_row.get("down_limit"))
                limit_ratio = round(abs((upper_limit / pre_close) - 1.0), 6) if pre_close > 0 else 0.0
            else:
                upper_limit = 0.0
                lower_limit = 0.0
                limit_ratio = 0.0
                missing_stk_limit_count += 1

            limit_up_hit = upper_limit > 0 and high >= upper_limit and close >= upper_limit
            limit_down_hit = lower_limit > 0 and low <= lower_limit and close <= lower_limit

            rows.append(
                {
                    "trade_date": trade_date.replace("-", ""),
                    "symbol": symbol,
                    "board": board,
                    "is_st": is_st,
                    "is_suspended": is_suspended,
                    "limit_ratio": limit_ratio,
                    "upper_limit_price": f"{_round_price(upper_limit):.2f}" if upper_limit > 0 else "0.00",
                    "lower_limit_price": f"{_round_price(lower_limit):.2f}" if lower_limit > 0 else "0.00",
                    "limit_up_hit": limit_up_hit,
                    "limit_down_hit": limit_down_hit,
                    "halt_or_suspend_flag": is_suspended,
                    "semantic_st_proxy": is_st,
                    "semantic_suspend_source": is_suspended,
                    "stk_limit_present": stk_limit_row is not None,
                }
            )

        residual_rows = [
            {
                "residual_class": "st_proxy_from_namechange_only",
                "residual_reason": "ST semantics are currently approximated from namechange history rather than a dedicated status master",
            },
            {
                "residual_class": "suspension_source_sparse",
                "residual_reason": "suspend_d is retained and usable but sparse, so suspension semantics remain event-like rather than complete market-state truth",
            },
            {
                "residual_class": "missing_stk_limit_rows",
                "residual_reason": "some daily rows may still miss stk_limit joins and therefore remain non-promotive for replay",
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
            "symbol_count": len({row["symbol"] for row in rows}),
            "coverage_start": min(row["trade_date"] for row in rows),
            "coverage_end": max(row["trade_date"] for row in rows),
            "st_proxy_row_count": st_proxy_row_count,
            "suspended_row_count": suspended_row_count,
            "missing_stk_limit_count": missing_stk_limit_count,
            "surface_path": str(self.surface_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareLimitHaltSemanticSurfaceV1(
            summary=summary, rows=rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareLimitHaltSemanticSurfaceV1(repo_root).materialize()
    print(result.summary["surface_path"])


if __name__ == "__main__":
    main()
