from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130RBK0808600118NearSurfaceWatchWindowAuditReport:
    summary: dict[str, Any]
    watch_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "watch_rows": self.watch_rows,
            "interpretation": self.interpretation,
        }


class V130RBK0808600118NearSurfaceWatchWindowAuditAnalyzer:
    TARGET_SYMBOL = "600118"
    TARGET_SECTOR = "BK0808"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.watch_path = repo_root / "reports" / "analysis" / "v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1.json"
        self.timeline_path = repo_root / "reports" / "analysis" / "market_v6_q3_symbol_timeline_600118_capture_c_v1.json"
        self.sector_path = (
            repo_root
            / "data"
            / "derived"
            / "sector_snapshots"
            / "market_research_sector_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.output_csv_path = repo_root / "data" / "training" / "bk0808_600118_near_surface_watch_window_v1.csv"

    def _load_daily_board_composite(self) -> dict[str, float]:
        by_date: dict[str, list[float]] = {}
        with self.sector_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["sector_id"] != self.TARGET_SECTOR:
                    continue
                composite = (
                    float(row["persistence"])
                    + float(row["diffusion"])
                    + float(row["money_making"])
                    + float(row["leader_strength"])
                    + float(row["relative_strength"])
                    + float(row["activity"])
                ) / 6.0
                by_date.setdefault(row["trade_date"], []).append(round(composite, 6))
        return {trade_date: round(sum(values) / len(values), 6) for trade_date, values in by_date.items()}

    def analyze(self) -> V130RBK0808600118NearSurfaceWatchWindowAuditReport:
        watch_report = json.loads(self.watch_path.read_text(encoding="utf-8"))
        target_row = next(row for row in watch_report["candidate_rows"] if row["symbol"] == self.TARGET_SYMBOL)
        timeline_payload = json.loads(self.timeline_path.read_text(encoding="utf-8"))
        board_composite_by_date = self._load_daily_board_composite()

        best_by_date: dict[str, dict[str, Any]] = {}
        for record in timeline_payload.get("candidate_records", []):
            for daily_row in record.get("daily_records", []):
                if daily_row.get("approved_sector_id") != self.TARGET_SECTOR:
                    continue
                trade_date = daily_row["trade_date"]
                assignment_layer = daily_row.get("assignment_layer")
                assignment_score = float(daily_row.get("assignment_score") or 0.0)
                board_composite = board_composite_by_date.get(trade_date)
                leader_core = assignment_layer in {"leader", "core"}
                board_strong = board_composite is not None and board_composite >= 0.45
                near_surface_watch_active = leader_core and assignment_score >= 0.45 and board_strong
                row = {
                    "trade_date": trade_date,
                    "symbol": self.TARGET_SYMBOL,
                    "assignment_layer": assignment_layer,
                    "assignment_score": round(assignment_score, 6),
                    "board_composite": board_composite,
                    "leader_core": leader_core,
                    "board_strong": board_strong,
                    "near_surface_watch_active": near_surface_watch_active,
                }
                prior = best_by_date.get(trade_date)
                prior_rank = 0 if prior is None else (
                    int(prior["near_surface_watch_active"]),
                    float(prior["assignment_score"]),
                )
                current_rank = (
                    int(near_surface_watch_active),
                    assignment_score,
                )
                if prior is None or current_rank > prior_rank:
                    best_by_date[trade_date] = row

        rows = sorted(best_by_date.values(), key=lambda row: row["trade_date"])
        rows.sort(key=lambda row: row["trade_date"])
        active_rows = [row for row in rows if row["near_surface_watch_active"]]
        summary = {
            "acceptance_posture": "freeze_v130r_bk0808_600118_near_surface_watch_window_audit_v1",
            "symbol": self.TARGET_SYMBOL,
            "watch_status": target_row["recommended_watch_status"],
            "timeline_approval_days": target_row["timeline_approval_days"],
            "timeline_leader_core_days": target_row["timeline_leader_core_days"],
            "near_surface_watch_day_count": len(active_rows),
            "near_surface_watch_first_date": active_rows[0]["trade_date"] if active_rows else None,
            "near_surface_watch_last_date": active_rows[-1]["trade_date"] if active_rows else None,
            "authoritative_status": "600118_has_real_near_surface_watch_windows_but_still_not_same_plane_support",
            "authoritative_rule": "use_near_surface_watch_windows_for_monitoring_only_until_v6_same_plane_snapshot_support_appears",
        }
        interpretation = [
            "V1.30R upgrades the BK0808 watch from a static candidate list into dated near-surface watch windows.",
            "600118 does not just have abstract timeline support; it has concrete windows where BK0808 board strength and leader/core status align.",
            "That still does not equal same-plane support, so the worker remains frozen.",
        ]
        return V130RBK0808600118NearSurfaceWatchWindowAuditReport(
            summary=summary,
            watch_rows=rows,
            interpretation=interpretation,
        )

    def write_watch_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130RBK0808600118NearSurfaceWatchWindowAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130RBK0808600118NearSurfaceWatchWindowAuditAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130r_bk0808_600118_near_surface_watch_window_audit_v1",
        result=result,
    )
    analyzer.write_watch_csv(result.watch_rows)


if __name__ == "__main__":
    main()
