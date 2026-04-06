from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pr_a_share_shadow_calendar_alignment_candidate_audit_v1 import (
    V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134PTAShareShadowEffectiveTradeDateTrialAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_replay_tradeable_context_binding_v1.csv"
        )
        self.semantic_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_semantic_surface_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_shadow_effective_trade_date_trial_status_v1.csv"
        )

    def analyze(self) -> V134PTAShareShadowEffectiveTradeDateTrialAuditV1Report:
        candidate_report = V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer(self.repo_root).analyze()
        candidate_row = candidate_report.rows[0]
        binding_rows = _read_csv(self.binding_path)
        semantic_rows = _read_csv(self.semantic_surface_path)
        semantic_dates = {
            f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}"
            for row in semantic_rows
            if row["trade_date"]
        }

        baseline_missing_count = sum(
            row["tradeable_context_state"] == "missing_tradeable_date_context" for row in binding_rows
        )
        trial_rows: list[dict[str, Any]] = []
        trial_bound_count = 0
        trial_missing_count = 0
        for row in binding_rows:
            if row["slice_id"] == candidate_row["slice_id"]:
                trial_query_date = candidate_row["candidate_effective_trade_date"]
                if trial_query_date in semantic_dates:
                    trial_state = "date_level_tradeable_context_bound_via_effective_trade_date"
                    trial_bound_count += 1
                else:
                    trial_state = row["tradeable_context_state"]
                    trial_missing_count += 1
            else:
                trial_query_date = row["decision_trade_date"]
                trial_state = row["tradeable_context_state"]
                if trial_state == "missing_tradeable_date_context":
                    trial_missing_count += 1
                else:
                    trial_bound_count += 1
            trial_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": row["decision_trade_date"],
                    "trial_query_trade_date": trial_query_date,
                    "baseline_tradeable_context_state": row["tradeable_context_state"],
                    "trial_tradeable_context_state": trial_state,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(trial_rows[0].keys()))
            writer.writeheader()
            writer.writerows(trial_rows)

        summary = {
            "baseline_missing_count": baseline_missing_count,
            "trial_missing_count": trial_missing_count,
            "trial_bound_count": trial_bound_count,
            "trial_improvement_count": baseline_missing_count - trial_missing_count,
            "candidate_effective_trade_date": candidate_row["candidate_effective_trade_date"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_effective_trade_date_trial_surface_materialized",
        }
        interpretation = [
            "A shadow-only effective-trade-date trial is enough to test the off-calendar slice without mutating PTI timestamps.",
            "The trial shows whether the candidate auxiliary trade date has real market-context recovery value before any production-facing change is considered.",
        ]
        return V134PTAShareShadowEffectiveTradeDateTrialAuditV1Report(
            summary=summary, rows=trial_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PTAShareShadowEffectiveTradeDateTrialAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pt_a_share_shadow_effective_trade_date_trial_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
