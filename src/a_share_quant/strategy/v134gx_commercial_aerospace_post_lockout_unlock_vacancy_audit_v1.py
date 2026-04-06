from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Report:
    summary: dict[str, Any]
    vacancy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "vacancy_rows": self.vacancy_rows,
            "interpretation": self.interpretation,
        }


class V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.lockout_path = analysis_dir / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        self.unlock_path = analysis_dir / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        self.expectancy_path = analysis_dir / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.phase_table_path = (
            repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"
        )
        self.intraday_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_lockout_unlock_vacancy_v1.csv"
        )

    def _build_trading_calendar(self) -> list[str]:
        return sorted({path.name.split("_")[0] for path in self.intraday_root.rglob("*_1min.zip")})

    def _load_csv_dates(self, path: Path) -> set[str]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return {row["trade_date"] for row in csv.DictReader(handle)}

    def analyze(self) -> V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Report:
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        expectancy = json.loads(self.expectancy_path.read_text(encoding="utf-8"))

        lockout_seed = lockout["seed_rows"][0]
        lockout_end = lockout_seed["lockout_end_trade_date"]
        trading_calendar = self._build_trading_calendar()
        post_lockout_dates = [trade_date for trade_date in trading_calendar if trade_date > lockout_end]

        daily_dates = self._load_csv_dates(self.daily_state_path)
        phase_dates = self._load_csv_dates(self.phase_table_path)
        unlock_positive_dates = {row["trade_date"] for row in unlock["positive_seed_rows"]}
        unlock_worthy_dates = {
            row["trade_date"]
            for row in expectancy["seed_rows"]
            if row["expectancy_state"] == "unlock_worthy"
        }

        vacancy_rows: list[dict[str, Any]] = []
        raw_only_vacancy_count = 0
        derived_board_surface_present_count = 0
        unlock_positive_post_lockout_count = 0
        unlock_worthy_post_lockout_count = 0

        for trade_date in post_lockout_dates:
            raw_intraday_present = True
            daily_surface_present = trade_date in daily_dates
            phase_surface_present = trade_date in phase_dates
            derived_board_surface_present = daily_surface_present and phase_surface_present
            unlock_positive = trade_date in unlock_positive_dates
            unlock_worthy = trade_date in unlock_worthy_dates

            if derived_board_surface_present:
                derived_board_surface_present_count += 1
            else:
                raw_only_vacancy_count += 1

            if unlock_positive:
                unlock_positive_post_lockout_count += 1
            if unlock_worthy:
                unlock_worthy_post_lockout_count += 1

            if not derived_board_surface_present:
                vacancy_family = "raw_only_post_lockout_vacancy"
                vacancy_reading = "intraday raw exists but board-level derived state surface is absent"
            elif not unlock_positive and not unlock_worthy:
                vacancy_family = "covered_but_no_unlock_context"
                vacancy_reading = "derived board surface exists but no unlock-positive or unlock-worthy context is present"
            else:
                vacancy_family = "unlock_context_present"
                vacancy_reading = "post-lockout day has both derived surface and board unlock context"

            vacancy_rows.append(
                {
                    "trade_date": trade_date,
                    "raw_intraday_present": raw_intraday_present,
                    "daily_surface_present": daily_surface_present,
                    "phase_surface_present": phase_surface_present,
                    "derived_board_surface_present": derived_board_surface_present,
                    "unlock_positive": unlock_positive,
                    "unlock_worthy": unlock_worthy,
                    "vacancy_family": vacancy_family,
                    "vacancy_reading": vacancy_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(vacancy_rows[0].keys()))
            writer.writeheader()
            writer.writerows(vacancy_rows)

        summary = {
            "acceptance_posture": "freeze_v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1",
            "lockout_end_trade_date": lockout_end,
            "post_lockout_trade_date_count": len(post_lockout_dates),
            "post_lockout_raw_intraday_count": len(post_lockout_dates),
            "derived_board_surface_present_count": derived_board_surface_present_count,
            "raw_only_vacancy_count": raw_only_vacancy_count,
            "post_lockout_unlock_positive_count": unlock_positive_post_lockout_count,
            "post_lockout_unlock_worthy_count": unlock_worthy_post_lockout_count,
            "vacancy_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "current post-lockout vacancy is not only absence of unlock seeds; local raw dates already exist, "
                "but no post-lockout derived board surface exists on which unlock context could be evaluated"
            ),
        }
        interpretation = [
            "V1.34GX asks a narrower question than handoff readiness: what exactly exists after lockout end?",
            "The answer is asymmetrical. Local intraday raw data continues after lockout, but the board-level derived state surface stops at lockout end, so unlock vacancy is currently a derived-context absence, not merely a weak-board reading.",
        ]
        return V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Report(
            summary=summary,
            vacancy_rows=vacancy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
