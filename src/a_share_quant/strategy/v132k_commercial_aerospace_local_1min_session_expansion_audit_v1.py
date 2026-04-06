from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1 import _predict_tier


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


@dataclass(slots=True)
class V132KCommercialAerospaceLocal1MinSessionExpansionAuditReport:
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


class V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_report_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )

    def analyze(self) -> V132KCommercialAerospaceLocal1MinSessionExpansionAuditReport:
        registry = json.loads(self.registry_report_path.read_text(encoding="utf-8"))
        seed_symbols = sorted({row["symbol"] for row in registry["registry_rows"]})

        hit_rows: list[dict[str, Any]] = []
        symbol_session_counts = {symbol: 0 for symbol in seed_symbols}
        symbol_hit_counts = {symbol: 0 for symbol in seed_symbols}

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
                        symbol_session_counts[symbol] += 1
                        with archive.open(member_name, "r") as member:
                            minute_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
                        if len(minute_rows) < 60:
                            continue
                        first_60 = minute_rows[:60]
                        base_open = float(first_60[0][3])
                        closes = [float(r[4]) for r in first_60]
                        highs = [float(r[5]) for r in first_60]
                        lows = [float(r[6]) for r in first_60]
                        full_day_close = float(minute_rows[-1][4])

                        close15 = closes[14]
                        close30 = closes[29]
                        close60 = closes[59]
                        low15 = min(lows[:15])
                        low60 = min(lows[:60])
                        high15 = max(highs[:15])
                        high60 = max(highs[:60])
                        close_loc15 = 0.5 if high15 == low15 else (close15 - low15) / (high15 - low15)
                        close_loc60 = 0.5 if high60 == low60 else (close60 - low60) / (high60 - low60)

                        feature_row = {
                            "open_to_close_return": full_day_close / base_open - 1.0,
                            "ret15": close15 / base_open - 1.0,
                            "ret30": close30 / base_open - 1.0,
                            "ret60": close60 / base_open - 1.0,
                            "draw60": low60 / base_open - 1.0,
                            "close_loc15": close_loc15,
                            "close_loc60": close_loc60,
                        }
                        predicted_tier = _predict_tier(feature_row)
                        if predicted_tier == "unmatched":
                            continue
                        symbol_hit_counts[symbol] += 1
                        hit_rows.append(
                            {
                                "trade_date": trade_date,
                                "month_bucket": f"{trade_date[:4]}-{trade_date[4:6]}",
                                "symbol": symbol,
                                "predicted_tier": predicted_tier,
                                **{k: round(v, 8) for k, v in feature_row.items()},
                            }
                        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if hit_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(hit_rows[0].keys()))
                writer.writeheader()
                writer.writerows(hit_rows)

        symbol_rows = []
        for symbol in seed_symbols:
            total = symbol_session_counts[symbol]
            hits = symbol_hit_counts[symbol]
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "session_count": total,
                    "hit_count": hits,
                    "hit_rate": round(hits / total, 8) if total else 0.0,
                }
            )

        tier_counts: dict[str, int] = {}
        for row in hit_rows:
            tier_counts[row["predicted_tier"]] = tier_counts.get(row["predicted_tier"], 0) + 1

        summary = {
            "acceptance_posture": "freeze_v132k_commercial_aerospace_local_1min_session_expansion_audit_v1",
            "seed_symbol_count": len(seed_symbols),
            "expanded_session_count": sum(symbol_session_counts.values()),
            "expanded_hit_count": len(hit_rows),
            "severe_hit_count": tier_counts.get("severe_override_positive", 0),
            "reversal_hit_count": tier_counts.get("reversal_watch", 0),
            "mild_hit_count": tier_counts.get("mild_override_watch", 0),
            "max_symbol_hit_rate": max((row["hit_rate"] for row in symbol_rows), default=0.0),
            "hit_rows_csv": str(self.output_csv.relative_to(self.repo_root)) if hit_rows else "",
            "authoritative_rule": "the first local 1min rules should next be judged by how sparse and concentrated they remain on the broader local session surface of the retained seed symbols",
        }
        interpretation = [
            "V1.32K expands the 1-minute rule candidates from the replay buy surface to all locally available first-hour sessions for the six retained seed symbols.",
            "The governance question is whether the rules remain sparse and interpretable when applied to the broader session surface instead of only replay-associated entries.",
        ]
        return V132KCommercialAerospaceLocal1MinSessionExpansionAuditReport(
            summary=summary,
            hit_rows=hit_rows,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132KCommercialAerospaceLocal1MinSessionExpansionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132k_commercial_aerospace_local_1min_session_expansion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
