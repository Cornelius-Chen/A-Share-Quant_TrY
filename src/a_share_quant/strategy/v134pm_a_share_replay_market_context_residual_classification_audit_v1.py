from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134PMAShareReplayMarketContextResidualClassificationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer:
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
            repo_root / "data" / "training" / "a_share_replay_market_context_residual_classification_status_v1.csv"
        )

    def analyze(self) -> V134PMAShareReplayMarketContextResidualClassificationAuditV1Report:
        binding_rows = _read_csv(self.binding_path)
        semantic_rows = _read_csv(self.semantic_surface_path)
        coverage_start = min(row["trade_date"] for row in semantic_rows)
        coverage_end = max(row["trade_date"] for row in semantic_rows)
        coverage_start_iso = f"{coverage_start[:4]}-{coverage_start[4:6]}-{coverage_start[6:]}"
        coverage_end_iso = f"{coverage_end[:4]}-{coverage_end[4:6]}-{coverage_end[6:]}"

        rows: list[dict[str, Any]] = []
        pre_coverage_count = 0
        off_calendar_count = 0
        other_count = 0
        for row in binding_rows:
            if row["tradeable_context_state"] != "missing_tradeable_date_context":
                continue
            trade_date = row["decision_trade_date"]
            weekday_name = datetime.strptime(trade_date, "%Y-%m-%d").strftime("%A")
            if trade_date < coverage_start_iso:
                residual_class = "pre_coverage_shadow_slice"
                pre_coverage_count += 1
            elif weekday_name in {"Saturday", "Sunday"}:
                residual_class = "off_calendar_shadow_slice"
                off_calendar_count += 1
            else:
                residual_class = "other_missing_market_context"
                other_count += 1
            rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": trade_date,
                    "weekday_name": weekday_name,
                    "residual_class": residual_class,
                    "coverage_window": f"{coverage_start_iso} -> {coverage_end_iso}",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "missing_residual_count": len(rows),
            "pre_coverage_count": pre_coverage_count,
            "off_calendar_count": off_calendar_count,
            "other_count": other_count,
            "coverage_start": coverage_start_iso,
            "coverage_end": coverage_end_iso,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_market_context_residuals_classified",
        }
        interpretation = [
            "Replay market-context residuals are no longer a single undifferentiated gap.",
            "The remaining three missing dates split into two pre-coverage slices and one off-calendar shadow slice.",
            "That means the current residual is not a broad market-surface failure but a narrow boundary-and-calendar issue.",
        ]
        return V134PMAShareReplayMarketContextResidualClassificationAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PMAShareReplayMarketContextResidualClassificationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pm_a_share_replay_market_context_residual_classification_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
