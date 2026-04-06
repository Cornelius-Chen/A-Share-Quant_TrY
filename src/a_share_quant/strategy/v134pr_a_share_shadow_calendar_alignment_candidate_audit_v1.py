from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134PRAShareShadowCalendarAlignmentCandidateAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.time_slice_path = (
            repo_root / "data" / "derived" / "info_center" / "time_slices" / "a_share_time_slice_view_v1.csv"
        )
        self.event_ledger_path = (
            repo_root / "data" / "reference" / "info_center" / "event_registry" / "a_share_pti_event_ledger_v1.csv"
        )
        self.semantic_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_semantic_surface_v1.csv"
        )
        self.binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_replay_tradeable_context_binding_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_shadow_calendar_alignment_candidate_status_v1.csv"
        )

    def analyze(self) -> V134PRAShareShadowCalendarAlignmentCandidateAuditV1Report:
        slice_rows = _read_csv(self.time_slice_path)
        ledger_rows = _read_csv(self.event_ledger_path)
        binding_rows = _read_csv(self.binding_path)
        semantic_rows = _read_csv(self.semantic_surface_path)

        target_slice = next(row for row in slice_rows if row["slice_id"] == "slice_20260328_194152")
        target_binding = next(row for row in binding_rows if row["slice_id"] == target_slice["slice_id"])
        decision_ts = target_slice["decision_ts"]
        decision_trade_date = decision_ts[:10]

        same_ts_events = [row for row in ledger_rows if row["decision_ts"] == decision_ts]
        semantic_dates = sorted(
            {
                f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}"
                for row in semantic_rows
                if row["trade_date"]
            }
        )
        prior_trade_dates = [trade_date for trade_date in semantic_dates if trade_date < decision_trade_date]
        nearest_prior_trade_date = prior_trade_dates[-1] if prior_trade_dates else ""

        rows = [
            {
                "slice_id": target_slice["slice_id"],
                "decision_ts": decision_ts,
                "decision_trade_date": decision_trade_date,
                "current_tradeable_context_state": target_binding["tradeable_context_state"],
                "same_timestamp_event_count": len(same_ts_events),
                "nearest_prior_trade_date": nearest_prior_trade_date,
                "alignment_candidate_state": "auxiliary_effective_trade_date_candidate",
                "candidate_effective_trade_date": nearest_prior_trade_date,
                "timestamp_policy": "retain_visible_event_timestamp",
            }
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "candidate_row_count": len(rows),
            "same_timestamp_event_count": len(same_ts_events),
            "nearest_prior_trade_date": nearest_prior_trade_date,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_calendar_alignment_candidate_surface_materialized",
        }
        interpretation = [
            "The off-calendar replay residual is not evidence that the event timestamp is wrong; it is evidence that the replay lane may need an auxiliary market-alignment date.",
            "The current best candidate is to retain the visible Saturday timestamp while optionally mapping replay market context to the nearest prior trade date.",
            "That keeps PTI legality intact while opening a narrow shadow-only calendar-alignment inspection lane.",
        ]
        return V134PRAShareShadowCalendarAlignmentCandidateAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PRAShareShadowCalendarAlignmentCandidateAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pr_a_share_shadow_calendar_alignment_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
