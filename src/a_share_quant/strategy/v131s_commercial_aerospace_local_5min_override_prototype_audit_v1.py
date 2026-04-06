from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
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


def _resample_to_5min(rows: list[list[str]]) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in rows:
        ts = datetime.strptime(row[0], "%Y/%m/%d %H:%M")
        bucket = ts.replace(minute=(ts.minute // 5) * 5)
        op = float(row[3])
        cl = float(row[4])
        hi = float(row[5])
        lo = float(row[6])
        vol = float(row[7])
        amt = float(row[8])
        if current is None or current["bucket_dt"] != bucket:
            current = {
                "bucket_dt": bucket,
                "bucket": bucket.strftime("%H:%M"),
                "open": op,
                "high": hi,
                "low": lo,
                "close": cl,
                "volume": vol,
                "amount": amt,
            }
            bars.append(current)
            continue
        current["high"] = max(current["high"], hi)
        current["low"] = min(current["low"], lo)
        current["close"] = cl
        current["volume"] += vol
        current["amount"] += amt
    return bars


def _compute_features(bars: list[dict[str, Any]]) -> dict[str, float]:
    open_px = bars[0]["open"]
    close15 = bars[min(2, len(bars) - 1)]["close"]
    close30 = bars[min(5, len(bars) - 1)]["close"]
    close60 = bars[min(11, len(bars) - 1)]["close"]
    low15 = min(bar["low"] for bar in bars[:3])
    high15 = max(bar["high"] for bar in bars[:3])
    low60 = min(bar["low"] for bar in bars[:12])
    high60 = max(bar["high"] for bar in bars[:12])
    close_loc15 = 0.5 if high15 == low15 else (close15 - low15) / (high15 - low15)
    close_loc60 = 0.5 if high60 == low60 else (close60 - low60) / (high60 - low60)
    return {
        "ret15": close15 / open_px - 1.0,
        "ret30": close30 / open_px - 1.0,
        "ret60": close60 / open_px - 1.0,
        "draw15": low15 / open_px - 1.0,
        "draw60": low60 / open_px - 1.0,
        "close_loc15": close_loc15,
        "close_loc60": close_loc60,
    }


def _prototype_flag(features: dict[str, float]) -> bool:
    hard_open_collapse = features["ret15"] <= -0.05 and features["close_loc15"] <= 0.15
    persistent_hour_weakness = (
        features["ret60"] <= -0.045
        and features["draw60"] <= -0.045
        and features["close_loc60"] <= 0.10
    )
    return hard_open_collapse or persistent_hour_weakness


@dataclass(slots=True)
class V131SCommercialAerospaceLocal5MinOverridePrototypeAuditReport:
    summary: dict[str, Any]
    prototype_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "prototype_rows": self.prototype_rows,
            "interpretation": self.interpretation,
        }


class V131SCommercialAerospaceLocal5MinOverridePrototypeAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervision_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_override_supervision_rows_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_5min_override_prototype_rows_v1.csv"
        )

    def analyze(self) -> V131SCommercialAerospaceLocal5MinOverridePrototypeAuditReport:
        with self.supervision_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            supervision_rows = list(csv.DictReader(handle))

        prototype_rows: list[dict[str, Any]] = []
        for row in supervision_rows:
            trade_date = row["execution_trade_date"]
            zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
            member_name = _symbol_to_archive_member(row["symbol"])
            with zipfile.ZipFile(zip_path) as archive:
                with archive.open(member_name, "r") as member:
                    rows_1m = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
            bars_5m = _resample_to_5min(rows_1m)
            features = _compute_features(bars_5m)
            prototype_rows.append(
                {
                    **row,
                    **features,
                    "prototype_flag": _prototype_flag(features),
                    "five_minute_row_count": len(bars_5m),
                    "sample_5min_head": json.dumps(
                        [{k: v for k, v in bar.items() if k != "bucket_dt"} for bar in bars_5m[:3]],
                        ensure_ascii=False,
                    ),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(prototype_rows[0].keys()))
            writer.writeheader()
            for row in prototype_rows:
                writer.writerow(row)

        def _count(label: str, *, flagged: bool | None = None) -> int:
            rows = [row for row in prototype_rows if row["supervision_label"] == label]
            if flagged is None:
                return len(rows)
            return sum(1 for row in rows if bool(row["prototype_flag"]) is flagged)

        summary = {
            "acceptance_posture": "freeze_v131s_commercial_aerospace_local_5min_override_prototype_audit_v1",
            "prototype_rows_csv": str(self.output_csv.relative_to(self.repo_root)),
            "override_positive_hit_count": _count("override_positive", flagged=True),
            "override_positive_total": _count("override_positive"),
            "reversal_watch_hit_count": _count("reversal_watch", flagged=True),
            "reversal_watch_total": _count("reversal_watch"),
            "clean_control_hit_count": _count("clean_control", flagged=True),
            "clean_control_total": _count("clean_control"),
            "ambiguous_hit_count": _count("ambiguous_non_override", flagged=True),
            "ambiguous_total": _count("ambiguous_non_override"),
            "mismatch_watch_hit_count": _count("mismatch_watch", flagged=True),
            "mismatch_watch_total": _count("mismatch_watch"),
            "authoritative_rule": "a narrow 5min collapse-override prototype should catch retained override positives and reversal watches while staying off clean controls",
        }
        interpretation = [
            "V1.31S formalizes the first narrow commercial-aerospace 5-minute collapse-override prototype using only the locally available retained supervision set.",
            "The prototype is intentionally governance-bound: it is designed to classify obvious intraday collapses, not to rewrite the lawful EOD primary.",
        ]
        return V131SCommercialAerospaceLocal5MinOverridePrototypeAuditReport(
            summary=summary,
            prototype_rows=prototype_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131SCommercialAerospaceLocal5MinOverridePrototypeAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131SCommercialAerospaceLocal5MinOverridePrototypeAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131s_commercial_aerospace_local_5min_override_prototype_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
