from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Report:
    summary: dict[str, Any]
    gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "gap_rows": self.gap_rows,
            "interpretation": self.interpretation,
        }


class V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.lockout_path = analysis_dir / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.phase_table_path = (
            repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"
        )
        self.intraday_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_board_surface_derivation_gap_v1.csv"
        )

    def _build_raw_calendar(self) -> list[str]:
        return sorted({path.name.split("_")[0] for path in self.intraday_root.rglob("*_1min.zip")})

    def _load_csv_dates(self, path: Path) -> list[str]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [row["trade_date"] for row in csv.DictReader(handle)]

    def analyze(self) -> V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Report:
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        lockout_end = lockout["seed_rows"][0]["lockout_end_trade_date"]

        raw_dates = self._build_raw_calendar()
        daily_dates = self._load_csv_dates(self.daily_state_path)
        phase_dates = self._load_csv_dates(self.phase_table_path)

        raw_last_trade_date = raw_dates[-1]
        daily_last_trade_date = daily_dates[-1]
        phase_last_trade_date = phase_dates[-1]

        post_lockout_raw_dates = [trade_date for trade_date in raw_dates if trade_date > lockout_end]
        daily_gap_dates = [trade_date for trade_date in post_lockout_raw_dates if trade_date not in set(daily_dates)]
        phase_gap_dates = [trade_date for trade_date in post_lockout_raw_dates if trade_date not in set(phase_dates)]

        synchronized_surface_stop = daily_last_trade_date == phase_last_trade_date == lockout_end
        gap_rows = [
            {
                "surface_name": "raw_intraday_calendar",
                "last_trade_date": raw_last_trade_date,
                "post_lockout_trade_date_count": len(post_lockout_raw_dates),
                "post_lockout_gap_count": 0,
                "stop_alignment": "continues_past_lockout_end",
                "gap_reading": "local raw calendar extends beyond lockout end",
            },
            {
                "surface_name": "daily_state_surface",
                "last_trade_date": daily_last_trade_date,
                "post_lockout_trade_date_count": len(post_lockout_raw_dates),
                "post_lockout_gap_count": len(daily_gap_dates),
                "stop_alignment": "stops_at_lockout_end" if daily_last_trade_date == lockout_end else "decoupled_stop",
                "gap_reading": "board daily-state derivation does not cover post-lockout raw dates",
            },
            {
                "surface_name": "phase_geometry_surface",
                "last_trade_date": phase_last_trade_date,
                "post_lockout_trade_date_count": len(post_lockout_raw_dates),
                "post_lockout_gap_count": len(phase_gap_dates),
                "stop_alignment": "stops_at_lockout_end" if phase_last_trade_date == lockout_end else "decoupled_stop",
                "gap_reading": "board phase-geometry derivation does not cover post-lockout raw dates",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(gap_rows[0].keys()))
            writer.writeheader()
            writer.writerows(gap_rows)

        summary = {
            "acceptance_posture": "freeze_v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1",
            "lockout_end_trade_date": lockout_end,
            "raw_last_trade_date": raw_last_trade_date,
            "daily_last_trade_date": daily_last_trade_date,
            "phase_last_trade_date": phase_last_trade_date,
            "post_lockout_raw_trade_date_count": len(post_lockout_raw_dates),
            "daily_post_lockout_gap_count": len(daily_gap_dates),
            "phase_post_lockout_gap_count": len(phase_gap_dates),
            "synchronized_surface_stop": synchronized_surface_stop,
            "first_post_lockout_gap_trade_date": post_lockout_raw_dates[0] if post_lockout_raw_dates else "",
            "last_post_lockout_gap_trade_date": post_lockout_raw_dates[-1] if post_lockout_raw_dates else "",
            "gap_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "post-lockout unlock vacancy is currently a synchronized board-surface derivation gap: raw intraday dates extend "
                "past lockout end, but both daily-state and phase-geometry surfaces stop exactly at the lockout boundary"
            ),
        }
        interpretation = [
            "V1.34GZ audits coverage rather than market meaning.",
            "It shows whether the shadow replay lane is blocked by weak post-lockout context or by the simpler fact that the board-level derived surfaces were never extended beyond the lockout end date.",
        ]
        return V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Report(
            summary=summary,
            gap_rows=gap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
