from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    rebound_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "rebound_rows": self.rebound_rows,
            "interpretation": self.interpretation,
        }


class V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_local_binding_attribution_v1.csv"
        )

    def analyze(self) -> V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        session_rows = audit["session_rows"]

        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in session_rows:
            buckets[row["symbol"]].append(row)

        symbol_rows: list[dict[str, Any]] = []
        for symbol, subset in sorted(buckets.items()):
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "session_count": len(subset),
                    "same_day_protected_mark_to_close_total": round(
                        sum(float(row["same_day_protected_mark_to_close"]) for row in subset),
                        4,
                    ),
                    "net_horizon_pnl_if_held_1d": round(
                        sum(float(row["horizon_pnl_if_held_1d"]) for row in subset if row["horizon_pnl_if_held_1d"] != ""),
                        4,
                    ),
                    "net_horizon_pnl_if_held_3d": round(
                        sum(float(row["horizon_pnl_if_held_3d"]) for row in subset if row["horizon_pnl_if_held_3d"] != ""),
                        4,
                    ),
                    "net_horizon_pnl_if_held_5d": round(
                        sum(float(row["horizon_pnl_if_held_5d"]) for row in subset if row["horizon_pnl_if_held_5d"] != ""),
                        4,
                    ),
                    "positive_3d_rebound_case_count": sum(
                        1 for row in subset if row["horizon_pnl_if_held_3d"] != "" and float(row["horizon_pnl_if_held_3d"]) > 0
                    ),
                }
            )

        rebound_rows = sorted(
            [
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "predicted_tier": row["predicted_tier"],
                    "same_day_protected_mark_to_close": round(float(row["same_day_protected_mark_to_close"]), 4),
                    "horizon_pnl_if_held_3d": round(float(row["horizon_pnl_if_held_3d"]), 4),
                }
                for row in session_rows
                if row["horizon_pnl_if_held_3d"] != "" and float(row["horizon_pnl_if_held_3d"]) > 0
            ],
            key=lambda row: float(row["horizon_pnl_if_held_3d"]),
            reverse=True,
        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        best_same_day_symbol = max(symbol_rows, key=lambda row: float(row["same_day_protected_mark_to_close_total"]))
        worst_3d_symbol = max(symbol_rows, key=lambda row: float(row["net_horizon_pnl_if_held_3d"]))
        top_rebound_case = rebound_rows[0] if rebound_rows else None

        summary = {
            "acceptance_posture": "freeze_v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1",
            "executed_order_count": len(session_rows),
            "best_same_day_symbol": best_same_day_symbol["symbol"],
            "worst_3d_rebound_symbol": worst_3d_symbol["symbol"],
            "positive_3d_rebound_case_count": len(rebound_rows),
            "top_3d_rebound_case": (
                f"{top_rebound_case['trade_date']} {top_rebound_case['symbol']}"
                if top_rebound_case
                else ""
            ),
            "attribution_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_isolated_sell_side_local_binding_attribution_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CH decomposes the first isolated sell-side binding surface into same-day protection contributors and 3-day rebound-cost residues.",
            "The point is to identify whether the remaining medium-short caveat is broad or concentrated enough for strictly local supervision only.",
        ]
        return V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            rebound_rows=rebound_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
