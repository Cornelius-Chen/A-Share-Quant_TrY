from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditReport:
    summary: dict[str, Any]
    support_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "support_rows": self.support_rows,
            "interpretation": self.interpretation,
        }


class V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditAnalyzer:
    FOCUS_START = "20251114"
    FOCUS_END = "20260112"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.training_table_path = repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"

    def analyze(self) -> V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditReport:
        rows = _load_csv(self.training_table_path)
        ordered_dates = sorted({row["trade_date"] for row in rows})
        date_to_idx = {trade_date: idx for idx, trade_date in enumerate(ordered_dates)}
        by_date: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            by_date.setdefault(row["trade_date"], []).append(row)

        focus_dates = [d for d in ordered_dates if self.FOCUS_START <= d <= self.FOCUS_END]
        support_rows: list[dict[str, Any]] = []
        for trade_date in focus_dates:
            idx = date_to_idx[trade_date]
            mature_cutoff_idx = idx - 10
            mature_dates = set(ordered_dates[: mature_cutoff_idx + 1]) if mature_cutoff_idx >= 0 else set()
            matured = [row for row in rows if row["trade_date"] in mature_dates]
            matured_full = [row for row in matured if row["supervised_action_label_pg"] == "full_eligibility_target"]
            matured_probe = [row for row in matured if row["supervised_action_label_pg"] == "probe_eligibility_target"]
            matured_preheat_full = [row for row in matured_full if row["phase_window_semantic"] == "preheat_window"]
            support_rows.append(
                {
                    "trade_date": trade_date,
                    "matured_full_count": len(matured_full),
                    "matured_probe_count": len(matured_probe),
                    "matured_preheat_full_count": len(matured_preheat_full),
                    "focus_date_regime_mix": dict(Counter(row["regime_proxy_semantic"] for row in by_date.get(trade_date, []))),
                }
            )

        earliest_with_full = next((row["trade_date"] for row in support_rows if row["matured_full_count"] > 0), "")
        summary = {
            "acceptance_posture": "freeze_v126n_commercial_aerospace_phase_geometry_walk_forward_support_audit_v1",
            "focus_start": self.FOCUS_START,
            "focus_end": self.FOCUS_END,
            "earliest_trade_date_with_matured_full_support": earliest_with_full,
            "matured_full_count_on_20251224": next((row["matured_full_count"] for row in support_rows if row["trade_date"] == "20251224"), 0),
            "matured_preheat_full_count_on_20251224": next((row["matured_preheat_full_count"] for row in support_rows if row["trade_date"] == "20251224"), 0),
            "matured_full_count_on_20260108": next((row["matured_full_count"] for row in support_rows if row["trade_date"] == "20260108"), 0),
            "authoritative_rule": "commercial_aerospace_phase_geometry_relabel_is_useful_only_if_it_creates_matured_full_support_before_or_during_impulse_replay_dates",
        }
        interpretation = [
            "V1.26N checks the lawful walk-forward consequence of the new phase-geometry labels.",
            "The key question is whether preheat relabeling creates matured full-support before the impulse replay window rather than only after it.",
        ]
        return V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditReport(
            summary=summary,
            support_rows=support_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126n_commercial_aerospace_phase_geometry_walk_forward_support_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
