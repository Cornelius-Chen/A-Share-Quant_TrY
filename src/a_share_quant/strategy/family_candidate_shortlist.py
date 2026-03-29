from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FamilyCandidateShortlistReport:
    summary: dict[str, Any]
    shortlist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "shortlist_rows": self.shortlist_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FamilyCandidateShortlistAnalyzer:
    """Rank next symbol candidates for family-level replay work."""

    def analyze(
        self,
        *,
        report_specs: list[dict[str, Any]],
        excluded_symbols: list[dict[str, Any]],
        min_positive_delta: float = 0.0,
    ) -> FamilyCandidateShortlistReport:
        excluded = {
            (
                str(item["dataset_name"]),
                str(item["slice_name"]),
                str(item["strategy_name"]),
                str(item["symbol"]),
            )
            for item in excluded_symbols
        }

        shortlist_rows: list[dict[str, Any]] = []
        for spec in report_specs:
            payload = load_json_report(Path(str(spec["report_path"])))
            dataset_name = str(spec["dataset_name"])
            slice_name = str(spec["slice_name"])
            strategy_name = str(spec["strategy_name"])

            for row in payload.get("strategy_symbol_summary", []):
                symbol = str(row["symbol"])
                key = (dataset_name, slice_name, strategy_name, symbol)
                pnl_delta = float(row["pnl_delta"])
                incumbent_trade_count = int(row["incumbent_trade_count"])
                challenger_trade_count = int(row["challenger_trade_count"])
                if key in excluded:
                    continue
                if pnl_delta < min_positive_delta:
                    continue
                if incumbent_trade_count <= 0 or challenger_trade_count <= 0:
                    continue

                trade_count_gap = abs(incumbent_trade_count - challenger_trade_count)
                shortlist_score = pnl_delta / (1 + trade_count_gap)
                shortlist_rows.append(
                    {
                        "dataset_name": dataset_name,
                        "slice_name": slice_name,
                        "strategy_name": strategy_name,
                        "symbol": symbol,
                        "pnl_delta": round(pnl_delta, 6),
                        "incumbent_trade_count": incumbent_trade_count,
                        "challenger_trade_count": challenger_trade_count,
                        "trade_count_gap": trade_count_gap,
                        "incumbent_avg_holding_days": float(row["incumbent_avg_holding_days"]),
                        "challenger_avg_holding_days": float(row["challenger_avg_holding_days"]),
                        "shortlist_score": round(shortlist_score, 6),
                    }
                )

        shortlist_rows.sort(
            key=lambda item: (
                -float(item["shortlist_score"]),
                -float(item["pnl_delta"]),
                int(item["trade_count_gap"]),
            )
        )

        summary = {
            "candidate_count": len(shortlist_rows),
            "top_candidate": shortlist_rows[0] if shortlist_rows else None,
            "exclusion_count": len(excluded),
        }
        interpretation = [
            "Candidates stay on the shortlist only if both incumbent and challenger actually traded the symbol; pure suppression cases are excluded.",
            "The shortlist prefers large positive pnl deltas but discounts large trade-count gaps, because mixed churn often hides noisy multi-family pockets.",
            "A shortlist row is not proof of a reusable family. It is only a replay priority hint.",
        ]
        return FamilyCandidateShortlistReport(
            summary=summary,
            shortlist_rows=shortlist_rows,
            interpretation=interpretation,
        )


def write_family_candidate_shortlist_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FamilyCandidateShortlistReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
