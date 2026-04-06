from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Report:
    summary: dict[str, Any]
    readiness_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "readiness_rows": self.readiness_rows,
            "interpretation": self.interpretation,
        }


class V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.shadow_surface_path = (
            analysis_dir / "v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1.json"
        )
        self.unlock_path = analysis_dir / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        self.expectancy_path = analysis_dir / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        self.lockout_path = analysis_dir / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        self.intraday_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reentry_unlock_handoff_readiness_v1.csv"
        )

    def _build_trading_calendar(self) -> list[str]:
        trade_dates = {
            path.name.split("_")[0]
            for path in self.intraday_root.rglob("*_1min.zip")
        }
        return sorted(trade_dates)

    def _offset_trade_date(self, trading_calendar: list[str], trade_date: str, offset: int) -> str:
        idx = trading_calendar.index(trade_date)
        target_idx = min(idx + offset, len(trading_calendar) - 1)
        return trading_calendar[target_idx]

    def analyze(self) -> V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Report:
        surface = json.loads(self.shadow_surface_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        expectancy = json.loads(self.expectancy_path.read_text(encoding="utf-8"))
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        trading_calendar = self._build_trading_calendar()

        unlock_positive_dates = sorted(row["trade_date"] for row in unlock["positive_seed_rows"])
        unlock_worthy_dates = sorted(
            row["trade_date"]
            for row in expectancy["seed_rows"]
            if row["expectancy_state"] == "unlock_worthy"
        )
        lockout_start = lockout["seed_rows"][0]["lockout_start_trade_date"]
        lockout_end = lockout["seed_rows"][0]["lockout_end_trade_date"]

        readiness_rows: list[dict[str, Any]] = []
        lockout_overlap_block_count = 0
        no_future_unlock_seed_count = 0
        handoff_ready_count = 0

        for row in surface["state_rows"]:
            rebuild_watch_trade_date = self._offset_trade_date(
                trading_calendar,
                row["trade_date"],
                int(row["rebuild_watch_start_day"]),
            )
            future_unlock_positive_dates = [
                date for date in unlock_positive_dates if date >= rebuild_watch_trade_date
            ]
            future_unlock_worthy_dates = [
                date for date in unlock_worthy_dates if date >= rebuild_watch_trade_date
            ]
            lockout_overlap = rebuild_watch_trade_date <= lockout_end

            blocker_flags: list[str] = []
            if lockout_overlap:
                blocker_flags.append("lockout_overlap_block")
                lockout_overlap_block_count += 1
            if not future_unlock_positive_dates:
                blocker_flags.append("no_future_unlock_seed")
                no_future_unlock_seed_count += 1

            handoff_ready = len(blocker_flags) == 0
            if handoff_ready:
                handoff_ready_count += 1

            readiness_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "reentry_family": row["reentry_family"],
                    "board_gate_state": row["board_gate_state"],
                    "rebuild_watch_trade_date": rebuild_watch_trade_date,
                    "lockout_window": f"{lockout_start}->{lockout_end}",
                    "lockout_overlap": lockout_overlap,
                    "future_unlock_positive_count": len(future_unlock_positive_dates),
                    "future_unlock_worthy_count": len(future_unlock_worthy_dates),
                    "first_future_unlock_positive_trade_date": future_unlock_positive_dates[0] if future_unlock_positive_dates else "",
                    "first_future_unlock_worthy_trade_date": future_unlock_worthy_dates[0] if future_unlock_worthy_dates else "",
                    "handoff_ready": handoff_ready,
                    "blocker_family": "|".join(blocker_flags),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(readiness_rows[0].keys()))
            writer.writeheader()
            writer.writerows(readiness_rows)

        summary = {
            "acceptance_posture": "freeze_v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1",
            "seed_count": len(readiness_rows),
            "handoff_ready_count": handoff_ready_count,
            "lockout_overlap_block_count": lockout_overlap_block_count,
            "no_future_unlock_seed_count": no_future_unlock_seed_count,
            "unlock_positive_seed_count": unlock["summary"]["positive_seed_count"],
            "unlock_worthy_count": expectancy["summary"]["unlock_worthy_count"],
            "readiness_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "current reentry seeds are not blocked by vague caution but by explicit handoff-readiness gaps: "
                "their rebuild-watch dates still sit inside the lockout regime and no future unlock seed exists after those dates"
            ),
        }
        interpretation = [
            "V1.34GV turns the first bridge state surface into an explicit handoff-readiness audit.",
            "It asks the concrete next question: after rebuild watch begins, is there actually a later board-unlock context in which add permission could be consulted? For the current seeds, the answer is no.",
        ]
        return V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Report(
            summary=summary,
            readiness_rows=readiness_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
