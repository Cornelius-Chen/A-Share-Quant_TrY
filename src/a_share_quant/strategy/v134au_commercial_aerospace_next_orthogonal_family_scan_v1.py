from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import (
    _running_state,
    _symbol_to_archive_member,
)


@dataclass(slots=True)
class V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    hit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "hit_rows": self.hit_rows,
            "interpretation": self.interpretation,
        }


class V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )
        self.local_deferral_path = (
            repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_next_orthogonal_family_scan_v1.csv"
        )

    def _session_metrics(self, trade_date: str, symbol: str) -> dict[str, int]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]

        base_open = float(raw_rows[0][3])
        highs: list[float] = []
        lows: list[float] = []
        prev_state = "neutral"
        transition_count = 0
        reversal_entries = 0
        severe_entries = 0
        neutral_entries = 0
        for row in raw_rows[:240]:
            close_px = float(row[4])
            high_px = float(row[5])
            low_px = float(row[6])
            highs.append(high_px)
            lows.append(low_px)
            high_so_far = max(highs)
            low_so_far = min(lows)
            close_location = 0.5 if high_so_far == low_so_far else (close_px - low_so_far) / (high_so_far - low_so_far)
            state = _running_state(
                current_return=close_px / base_open - 1.0,
                drawdown=low_so_far / base_open - 1.0,
                close_location=close_location,
            )
            if state != prev_state:
                transition_count += 1
                if state == "reversal_watch":
                    reversal_entries += 1
                if state == "severe_override_positive":
                    severe_entries += 1
                if state == "neutral":
                    neutral_entries += 1
                prev_state = state
        return {
            "transition_count": transition_count,
            "reversal_entries": reversal_entries,
            "severe_entries": severe_entries,
            "neutral_entries": neutral_entries,
        }

    def analyze(self) -> V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Report:
        matched_keys = {
            (row["trade_date"], row["symbol"])
            for row in json.loads(self.local_deferral_path.read_text(encoding="utf-8"))["impacted_rows"]
        }
        session_rows: list[dict[str, Any]] = []
        with self.horizon_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if not row["horizon_pnl_5d"]:
                    continue
                trade_date = row["trade_date"]
                symbol = row["symbol"]
                is_rebound_cost = float(row["horizon_pnl_5d"]) > 0 and (trade_date, symbol) not in matched_keys
                metrics = self._session_metrics(trade_date, symbol)
                session_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "month_bucket": row["month_bucket"],
                        "is_remaining_rebound_cost": is_rebound_cost,
                        "horizon_pnl_5d": float(row["horizon_pnl_5d"]),
                        **metrics,
                    }
                )

        candidate_specs = [
            {"transition_floor": 25, "reversal_entry_floor": 10, "severe_entry_floor": 2},
            {"transition_floor": 30, "reversal_entry_floor": 15, "severe_entry_floor": 4},
            {"transition_floor": 35, "reversal_entry_floor": 18, "severe_entry_floor": 6},
        ]
        candidate_rows: list[dict[str, Any]] = []
        hit_sets: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
        for spec in candidate_specs:
            hits = [
                row
                for row in session_rows
                if row["transition_count"] >= spec["transition_floor"]
                and row["reversal_entries"] >= spec["reversal_entry_floor"]
                and row["severe_entries"] >= spec["severe_entry_floor"]
            ]
            rebound_hits = sum(1 for row in hits if row["is_remaining_rebound_cost"])
            other_hits = len(hits) - rebound_hits
            candidate_rows.append(
                {
                    **spec,
                    "matched_count": len(hits),
                    "remaining_rebound_cost_hit_count": rebound_hits,
                    "other_hit_count": other_hits,
                }
            )
            hit_sets[(spec["transition_floor"], spec["reversal_entry_floor"], spec["severe_entry_floor"])] = hits

        best_row = max(
            candidate_rows,
            key=lambda row: (
                row["remaining_rebound_cost_hit_count"],
                -row["other_hit_count"],
                row["transition_floor"],
            ),
        )
        best_key = (best_row["transition_floor"], best_row["reversal_entry_floor"], best_row["severe_entry_floor"])
        hit_rows = hit_sets[best_key]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()))
            writer.writeheader()
            writer.writerows(candidate_rows)

        summary = {
            "acceptance_posture": "freeze_v134au_commercial_aerospace_next_orthogonal_family_scan_v1",
            "remaining_rebound_cost_case_count": sum(1 for row in session_rows if row["is_remaining_rebound_cost"]),
            "best_transition_floor": best_row["transition_floor"],
            "best_reversal_entry_floor": best_row["reversal_entry_floor"],
            "best_severe_entry_floor": best_row["severe_entry_floor"],
            "best_remaining_rebound_cost_hit_count": best_row["remaining_rebound_cost_hit_count"],
            "best_other_hit_count": best_row["other_hit_count"],
            "candidate_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_next_orthogonal_family_scan_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AU scans for the next orthogonal supervision family after false-first-reversal reaches stopline.",
            "The candidate family here is oscillatory breakdown churn: many state flips, many reversal re-entries, and repeated severe participation.",
        ]
        return V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Report(
            summary=summary,
            candidate_rows=candidate_rows,
            hit_rows=hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AUCommercialAerospaceNextOrthogonalFamilyScanV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134au_commercial_aerospace_next_orthogonal_family_scan_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
