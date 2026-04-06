from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(slots=True)
class V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditReport:
    summary: dict[str, Any]
    session_feature_rows: list[dict[str, Any]]
    tier_envelope_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_feature_rows": self.session_feature_rows,
            "tier_envelope_rows": self.tier_envelope_rows,
            "interpretation": self.interpretation,
        }


class V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.seed_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_seed_windows_v1.csv"
        )

    @staticmethod
    def _first_breach(closes: list[float], base_open: float, threshold: float) -> int:
        for idx, close in enumerate(closes, start=1):
            if close / base_open - 1.0 <= threshold:
                return idx
        return 0

    def analyze(self) -> V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditReport:
        with self.seed_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for row in rows:
            key = (row["execution_trade_date"], row["symbol"], row["severity_tier"])
            grouped.setdefault(key, []).append(row)

        session_feature_rows: list[dict[str, Any]] = []
        for key, subset in sorted(grouped.items()):
            subset.sort(key=lambda row: int(row["minute_index"]))
            base_open = float(subset[0]["open"])
            closes = [float(row["close"]) for row in subset]
            highs = [float(row["high"]) for row in subset]
            lows = [float(row["low"]) for row in subset]
            red_flags = [1 if float(row["close"]) < float(row["open"]) else 0 for row in subset]

            low60 = min(lows)
            high60 = max(highs)
            minute_of_low60 = lows.index(low60) + 1
            minute_of_high60 = highs.index(high60) + 1
            close60 = closes[-1]
            bounce_from_low_to_close60 = close60 / low60 - 1.0 if low60 > 0 else 0.0
            red_share_15 = sum(red_flags[:15]) / 15.0
            red_share_60 = sum(red_flags) / len(red_flags)
            last10_return = close60 / closes[-10] - 1.0 if len(closes) >= 10 and closes[-10] > 0 else 0.0

            session_feature_rows.append(
                {
                    "execution_trade_date": key[0],
                    "symbol": key[1],
                    "severity_tier": key[2],
                    "first_breach_m2_minute": self._first_breach(closes, base_open, -0.02),
                    "first_breach_m4_minute": self._first_breach(closes, base_open, -0.04),
                    "minute_of_low60": minute_of_low60,
                    "minute_of_high60": minute_of_high60,
                    "red_share_15": round(red_share_15, 8),
                    "red_share_60": round(red_share_60, 8),
                    "bounce_from_low_to_close60": round(bounce_from_low_to_close60, 8),
                    "last10_return": round(last10_return, 8),
                    "close60_vs_open": round(close60 / base_open - 1.0, 8),
                    "low60_vs_open": round(low60 / base_open - 1.0, 8),
                }
            )

        tier_envelope_rows: list[dict[str, Any]] = []
        for tier in ["severe_override_positive", "reversal_watch", "mild_override_watch"]:
            subset = [row for row in session_feature_rows if row["severity_tier"] == tier]
            tier_envelope_rows.append(
                {
                    "severity_tier": tier,
                    "row_count": len(subset),
                    "first_breach_m2_minute_mean": round(mean(row["first_breach_m2_minute"] for row in subset), 8),
                    "first_breach_m4_minute_mean": round(mean(row["first_breach_m4_minute"] for row in subset), 8),
                    "minute_of_low60_mean": round(mean(row["minute_of_low60"] for row in subset), 8),
                    "red_share_15_mean": round(mean(row["red_share_15"] for row in subset), 8),
                    "red_share_60_mean": round(mean(row["red_share_60"] for row in subset), 8),
                    "bounce_from_low_to_close60_mean": round(
                        mean(row["bounce_from_low_to_close60"] for row in subset), 8
                    ),
                    "last10_return_mean": round(mean(row["last10_return"] for row in subset), 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1",
            "session_count": len(session_feature_rows),
            "severity_tier_count": len(tier_envelope_rows),
            "authoritative_rule": "the minute branch should characterize tier-specific first-hour envelopes before any later 1min formalization or governance expansion",
        }
        interpretation = [
            "V1.32E summarizes the local first-hour 1-minute seed windows into tier-specific pattern envelopes.",
            "The purpose is to identify whether severe, reversal, and mild watches differ not only by coarse return buckets but by when weakness appears, how persistent it is, and whether there is any meaningful bounce after the low.",
        ]
        return V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditReport(
            summary=summary,
            session_feature_rows=session_feature_rows,
            tier_envelope_rows=tier_envelope_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
