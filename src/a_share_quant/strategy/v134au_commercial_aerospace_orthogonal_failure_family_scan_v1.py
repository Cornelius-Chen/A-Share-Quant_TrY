from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import (
    _running_state,
    _symbol_to_archive_member,
)


@dataclass(slots=True)
class V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Report:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_orthogonal_failure_family_scan_v1.csv"
        )

    def _load_session_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        rows: list[dict[str, Any]] = []
        highs: list[float] = []
        lows: list[float] = []
        base_open = float(raw_rows[0][3])
        for idx, row in enumerate(raw_rows, start=1):
            close_px = float(row[4])
            high_px = float(row[5])
            low_px = float(row[6])
            highs.append(high_px)
            lows.append(low_px)
            high_so_far = max(highs)
            low_so_far = min(lows)
            close_location = 0.5 if high_so_far == low_so_far else (close_px - low_so_far) / (high_so_far - low_so_far)
            rows.append(
                {
                    "minute_index": idx,
                    "close_px": close_px,
                    "state": _running_state(
                        current_return=close_px / base_open - 1.0,
                        drawdown=low_so_far / base_open - 1.0,
                        close_location=close_location,
                    ),
                }
            )
        return rows

    def analyze(self) -> V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Report:
        with self.horizon_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            horizon_rows = [row for row in csv.DictReader(handle) if row["horizon_pnl_5d"]]

        session_rows: list[dict[str, Any]] = []
        for row in horizon_rows:
            trade_date = row["trade_date"]
            symbol = row["symbol"]
            reversal_minute = int(row["reversal_minute"])
            fill_price = float(row["fill_price"])
            path_rows = self._load_session_rows(trade_date, symbol)
            first_severe_minute = next(
                (int(r["minute_index"]) for r in path_rows if r["state"] == "severe_override_positive"),
                None,
            )
            first_hour_end = min(len(path_rows), reversal_minute + 60)
            post_reversal = path_rows[reversal_minute:first_hour_end]
            post_reversal_flip_count = sum(
                1 for idx in range(1, len(post_reversal)) if post_reversal[idx]["state"] != post_reversal[idx - 1]["state"]
            )
            post_reversal_neutral_minutes = sum(1 for r in post_reversal if r["state"] == "neutral")
            post_reversal_reclaim_share = (
                sum(1 for r in post_reversal if float(r["close_px"]) >= fill_price) / len(post_reversal) if post_reversal else 0.0
            )

            post_severe = []
            if first_severe_minute is not None:
                severe_end = min(len(path_rows), first_severe_minute + 60)
                post_severe = path_rows[first_severe_minute:severe_end]
            post_severe_neutral_minutes = sum(1 for r in post_severe if r["state"] == "neutral")
            post_severe_reversal_minutes = sum(1 for r in post_severe if r["state"] == "reversal_watch")
            post_severe_reclaim_share = (
                sum(1 for r in post_severe if float(r["close_px"]) >= fill_price) / len(post_severe) if post_severe else 0.0
            )

            session_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "month_bucket": row["month_bucket"],
                    "regime_label": "rebound_cost_case" if float(row["horizon_pnl_5d"]) > 0 else "followthrough_benefit_case",
                    "post_reversal_flip_count_60": post_reversal_flip_count,
                    "post_reversal_neutral_minutes_60": post_reversal_neutral_minutes,
                    "post_reversal_reclaim_share_60": round(post_reversal_reclaim_share, 6),
                    "first_severe_minute": first_severe_minute or "",
                    "post_severe_neutral_minutes_60": post_severe_neutral_minutes,
                    "post_severe_reversal_minutes_60": post_severe_reversal_minutes,
                    "post_severe_reclaim_share_60": round(post_severe_reclaim_share, 6),
                }
            )

        rebound_rows = [row for row in session_rows if row["regime_label"] == "rebound_cost_case"]
        follow_rows = [row for row in session_rows if row["regime_label"] == "followthrough_benefit_case"]

        def _gap(key: str, rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]]) -> float:
            return round(mean(float(row[key]) for row in rows_a) - mean(float(row[key]) for row in rows_b), 6)

        family_rows = [
            {
                "family_name": "reversal_reclaim_churn",
                "primary_feature": "post_reversal_reclaim_share_60",
                "support_feature": "post_reversal_flip_count_60",
                "primary_gap_rebound_minus_followthrough": _gap(
                    "post_reversal_reclaim_share_60", rebound_rows, follow_rows
                ),
                "support_gap_rebound_minus_followthrough": _gap(
                    "post_reversal_flip_count_60", rebound_rows, follow_rows
                ),
            },
            {
                "family_name": "early_severe_reclaim",
                "primary_feature": "post_severe_neutral_minutes_60",
                "support_feature": "post_severe_reversal_minutes_60",
                "primary_gap_rebound_minus_followthrough": _gap(
                    "post_severe_neutral_minutes_60",
                    [row for row in rebound_rows if row["first_severe_minute"] != ""],
                    [row for row in follow_rows if row["first_severe_minute"] != ""],
                ),
                "support_gap_rebound_minus_followthrough": _gap(
                    "post_severe_reversal_minutes_60",
                    [row for row in rebound_rows if row["first_severe_minute"] != ""],
                    [row for row in follow_rows if row["first_severe_minute"] != ""],
                ),
            },
        ]

        strongest = max(
            family_rows,
            key=lambda row: abs(float(row["primary_gap_rebound_minus_followthrough"])) + 0.01 * abs(float(row["support_gap_rebound_minus_followthrough"])),
        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        summary = {
            "acceptance_posture": "freeze_v134au_commercial_aerospace_orthogonal_failure_family_scan_v1",
            "reversal_session_count": len(session_rows),
            "rebound_cost_case_count": len(rebound_rows),
            "strongest_family_name": strongest["family_name"],
            "strongest_primary_gap": strongest["primary_gap_rebound_minus_followthrough"],
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_orthogonal_failure_family_scan_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AU does a quick orthogonal-family scan after the false-first-reversal family reached stopline.",
            "The goal is not to open a new branch immediately, but to verify whether any other failure family has enough separation to justify a first audit.",
        ]
        return V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Report(
            summary=summary,
            family_rows=family_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AUCommercialAerospaceOrthogonalFailureFamilyScanV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134au_commercial_aerospace_orthogonal_failure_family_scan_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
