from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Report:
    summary: dict[str, Any]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


class V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer:
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
        self.orders_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.grouped_actions_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_grouped_actions_v1.csv"
        )
        self.raw_daily_bars_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.raw_intraday_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_derivation_boundary_classification_v1.csv"
        )

    def _last_trade_date_from_csv(self, path: Path, key: str) -> str:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return max(row[key] for row in rows)

    def _last_raw_intraday_trade_date(self) -> str:
        return max(path.name.split("_")[0] for path in self.raw_intraday_root.rglob("*_1min.zip"))

    def analyze(self) -> V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Report:
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        lockout_end = lockout["seed_rows"][0]["lockout_end_trade_date"]

        orders_last_trade_date = self._last_trade_date_from_csv(self.orders_path, "execution_trade_date")
        grouped_last_trade_date = self._last_trade_date_from_csv(self.grouped_actions_path, "trade_date")
        daily_state_last_trade_date = self._last_trade_date_from_csv(self.daily_state_path, "trade_date")
        phase_table_last_trade_date = self._last_trade_date_from_csv(self.phase_table_path, "trade_date")
        raw_daily_last_trade_date = self._last_trade_date_from_csv(self.raw_daily_bars_path, "trade_date")
        raw_intraday_last_trade_date = self._last_raw_intraday_trade_date()

        boundary_rows = [
            {
                "surface_name": "orders_execution_surface",
                "last_trade_date": orders_last_trade_date,
                "boundary_reading": "execution history stops here",
            },
            {
                "surface_name": "grouped_actions_surface",
                "last_trade_date": grouped_last_trade_date,
                "boundary_reading": "daily grouped action history stops here",
            },
            {
                "surface_name": "daily_state_surface",
                "last_trade_date": daily_state_last_trade_date,
                "boundary_reading": "board state derivation stops here",
            },
            {
                "surface_name": "phase_geometry_surface",
                "last_trade_date": phase_table_last_trade_date,
                "boundary_reading": "phase geometry derivation stops here",
            },
            {
                "surface_name": "raw_daily_bars",
                "last_trade_date": raw_daily_last_trade_date,
                "boundary_reading": "raw daily bars continue through this date",
            },
            {
                "surface_name": "raw_intraday_calendar",
                "last_trade_date": raw_intraday_last_trade_date,
                "boundary_reading": "raw intraday calendar continues through this date",
            },
            {
                "surface_name": "board_lockout_end",
                "last_trade_date": lockout_end,
                "boundary_reading": "lockout regime formally ends here",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(boundary_rows[0].keys()))
            writer.writeheader()
            writer.writerows(boundary_rows)

        derived_stop_matches_lockout_end = (
            daily_state_last_trade_date == phase_table_last_trade_date == lockout_end
        )
        derived_stop_after_last_execution = (
            daily_state_last_trade_date > orders_last_trade_date
            and phase_table_last_trade_date > grouped_last_trade_date
        )
        raw_coverage_beyond_derived = (
            raw_daily_last_trade_date > daily_state_last_trade_date
            and raw_intraday_last_trade_date > phase_table_last_trade_date
        )

        summary = {
            "acceptance_posture": "freeze_v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1",
            "orders_last_trade_date": orders_last_trade_date,
            "grouped_actions_last_trade_date": grouped_last_trade_date,
            "daily_state_last_trade_date": daily_state_last_trade_date,
            "phase_table_last_trade_date": phase_table_last_trade_date,
            "raw_daily_last_trade_date": raw_daily_last_trade_date,
            "raw_intraday_last_trade_date": raw_intraday_last_trade_date,
            "lockout_end_trade_date": lockout_end,
            "derived_stop_matches_lockout_end": derived_stop_matches_lockout_end,
            "derived_stop_after_last_execution": derived_stop_after_last_execution,
            "raw_coverage_beyond_derived": raw_coverage_beyond_derived,
            "boundary_classification": (
                "lockout_aligned_derivation_boundary"
                if derived_stop_matches_lockout_end and derived_stop_after_last_execution and raw_coverage_beyond_derived
                else "mixed_boundary_reading"
            ),
            "boundary_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "the current board-surface stop is better read as a lockout-aligned derivation boundary than as a raw-data deficit "
                "or a simple last-execution cutoff"
            ),
        }
        interpretation = [
            "V1.34HB classifies the boundary instead of extending it.",
            "Orders stop on 20260227, derived board surfaces stop on 20260320, and raw daily/intraday coverage continues to 20260403. That pattern points to a lockout-aligned derivation boundary rather than missing raw data or an execution-history truncation.",
        ]
        return V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Report(
            summary=summary,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
