from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y/%m/%d %H:%M")


@dataclass(slots=True)
class V133SCommercialAerospacePointInTimeVisibilityAuditReport:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V133SCommercialAerospacePointInTimeVisibilityAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.feed_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_point_in_time_seed_feed_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_point_in_time_visibility_audit_v1.csv"
        )

    def analyze(self) -> V133SCommercialAerospacePointInTimeVisibilityAuditReport:
        rows: list[dict[str, Any]] = []
        with self.feed_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(row)

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in rows:
            key = (row["execution_trade_date"], row["symbol"])
            grouped.setdefault(key, []).append(row)

        session_rows: list[dict[str, Any]] = []
        same_bar_violation_count = 0
        path_cutoff_violation_count = 0
        lineage_monotonic_violation_count = 0
        event_visibility_violation_count = 0
        warmup_nonnull_violation_count = 0

        lagged_fields = [
            "ret_1m_lag1",
            "ret_3m_lag1",
            "ret_5m_lag1",
            "draw_from_open_lag1",
            "draw_15m_lag1",
            "draw_30m_lag1",
            "close_location_lag1",
        ]

        for (execution_trade_date, symbol), session in grouped.items():
            session = sorted(session, key=lambda item: int(item["minute_index"]))
            session_open_ts = _parse_ts(session[0]["minute_ts"])

            session_same_bar_violations = 0
            session_path_cutoff_violations = 0
            session_lineage_monotonic_violations = 0
            session_event_visibility_violations = 0
            session_warmup_nonnull_violations = 0

            for row in session:
                minute_index = int(row["minute_index"])
                minute_ts = _parse_ts(row["minute_ts"])
                bar_first_visible_ts = _parse_ts(row["bar_first_visible_ts"])
                bar_source_cutoff_ts = _parse_ts(row["bar_source_cutoff_ts"])
                path_first_visible_ts = _parse_ts(row["path_feature_first_visible_ts"])
                path_source_cutoff_ts = _parse_ts(row["path_feature_source_cutoff_ts"])
                event_first_visible_ts = _parse_ts(row["event_state_first_visible_ts"])
                preopen_first_visible_ts = _parse_ts(row["pre_open_status_first_visible_ts"])
                phase_first_visible_ts = _parse_ts(row["phase_state_first_visible_ts"])

                if bar_first_visible_ts != minute_ts or bar_source_cutoff_ts != minute_ts:
                    session_same_bar_violations += 1

                if path_first_visible_ts is None or path_first_visible_ts != minute_ts:
                    session_lineage_monotonic_violations += 1

                if event_first_visible_ts is None or phase_first_visible_ts is None or preopen_first_visible_ts is None:
                    session_event_visibility_violations += 1
                else:
                    if event_first_visible_ts < session_open_ts or phase_first_visible_ts < session_open_ts or preopen_first_visible_ts < session_open_ts:
                        session_event_visibility_violations += 1

                non_null_lagged = any(row[field] not in ("", None) for field in lagged_fields)
                if non_null_lagged:
                    if path_source_cutoff_ts is None or minute_ts is None or not (path_source_cutoff_ts < minute_ts):
                        session_path_cutoff_violations += 1
                else:
                    # Warm-up nulls are fine, but they should only occur very early.
                    if minute_index > 6:
                        session_warmup_nonnull_violations += 1

            same_bar_violation_count += session_same_bar_violations
            path_cutoff_violation_count += session_path_cutoff_violations
            lineage_monotonic_violation_count += session_lineage_monotonic_violations
            event_visibility_violation_count += session_event_visibility_violations
            warmup_nonnull_violation_count += session_warmup_nonnull_violations

            session_rows.append(
                {
                    "execution_trade_date": execution_trade_date,
                    "symbol": symbol,
                    "minute_row_count": len(session),
                    "same_bar_violation_count": session_same_bar_violations,
                    "path_cutoff_violation_count": session_path_cutoff_violations,
                    "lineage_monotonic_violation_count": session_lineage_monotonic_violations,
                    "event_visibility_violation_count": session_event_visibility_violations,
                    "warmup_nonnull_violation_count": session_warmup_nonnull_violations,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        acceptance_rows = [
            {
                "acceptance_item": "same_bar_activation",
                "status": "pass" if same_bar_violation_count == 0 else "fail",
                "detail": f"same_bar_violation_count = {same_bar_violation_count}",
            },
            {
                "acceptance_item": "path_cutoff_precedes_visibility",
                "status": "pass" if path_cutoff_violation_count == 0 else "fail",
                "detail": f"path_cutoff_violation_count = {path_cutoff_violation_count}",
            },
            {
                "acceptance_item": "lineage_monotonicity",
                "status": "pass" if lineage_monotonic_violation_count == 0 else "fail",
                "detail": f"lineage_monotonic_violation_count = {lineage_monotonic_violation_count}",
            },
            {
                "acceptance_item": "event_visibility_from_session_open_or_later",
                "status": "pass" if event_visibility_violation_count == 0 else "fail",
                "detail": f"event_visibility_violation_count = {event_visibility_violation_count}",
            },
            {
                "acceptance_item": "warmup_nulls_bounded",
                "status": "pass" if warmup_nonnull_violation_count == 0 else "fail",
                "detail": f"warmup_nonnull_violation_count = {warmup_nonnull_violation_count}",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v133s_commercial_aerospace_point_in_time_visibility_audit_v1",
            "seed_session_count": len(session_rows),
            "same_bar_violation_count": same_bar_violation_count,
            "path_cutoff_violation_count": path_cutoff_violation_count,
            "lineage_monotonic_violation_count": lineage_monotonic_violation_count,
            "event_visibility_violation_count": event_visibility_violation_count,
            "warmup_nonnull_violation_count": warmup_nonnull_violation_count,
            "audit_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_point_in_time_visibility_seed_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.33S audits whether the canonical seed visibility feed actually obeys the phase-1 point-in-time rules.",
            "The goal is not performance but legality: same-bar activation, lagged-only path construction, and explicit lineage discipline.",
        ]
        return V133SCommercialAerospacePointInTimeVisibilityAuditReport(
            summary=summary,
            session_rows=session_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133SCommercialAerospacePointInTimeVisibilityAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133SCommercialAerospacePointInTimeVisibilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133s_commercial_aerospace_point_in_time_visibility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
