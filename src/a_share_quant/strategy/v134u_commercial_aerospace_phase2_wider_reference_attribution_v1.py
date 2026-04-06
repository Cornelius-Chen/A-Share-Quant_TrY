from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134UCommercialAerospacePhase2WiderReferenceAttributionReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    month_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "symbol_rows": self.symbol_rows,
            "month_rows": self.month_rows,
            "interpretation": self.interpretation,
        }


class V134UCommercialAerospacePhase2WiderReferenceAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_mild_block_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_wider_reference_attribution_v1.csv"
        )

    @staticmethod
    def _aggregate_rows(rows: list[dict[str, Any]], key_name: str) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            buckets[row[key_name]].append(row)

        total_avoided = sum(float(row["same_day_loss_avoided"]) for row in rows)
        out_rows: list[dict[str, Any]] = []
        for key, subset in sorted(buckets.items()):
            same_day_loss_avoided = sum(float(row["same_day_loss_avoided"]) for row in subset)
            out_rows.append(
                {
                    key_name: key,
                    "session_count": len(subset),
                    "same_day_loss_avoided_total": round(same_day_loss_avoided, 4),
                    "same_day_loss_avoided_share": round(same_day_loss_avoided / total_avoided, 8) if total_avoided else 0.0,
                    "positive_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) > 0),
                    "zero_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) == 0),
                    "negative_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) < 0),
                }
            )
        return out_rows

    def analyze(self) -> V134UCommercialAerospacePhase2WiderReferenceAttributionReport:
        with self.sessions_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            session_rows = list(csv.DictReader(handle))

        tier_rows = self._aggregate_rows(session_rows, "predicted_tier")
        symbol_rows = self._aggregate_rows(session_rows, "symbol")
        month_rows = self._aggregate_rows(session_rows, "month_bucket")

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        best_symbol = max(symbol_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        worst_symbol = min(symbol_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        best_month = max(month_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        worst_month = min(month_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))

        summary = {
            "acceptance_posture": "freeze_v134u_commercial_aerospace_phase2_wider_reference_attribution_v1",
            "session_count": len(session_rows),
            "same_day_loss_avoided_total": round(sum(float(row["same_day_loss_avoided"]) for row in session_rows), 4),
            "best_symbol": best_symbol["symbol"],
            "worst_symbol": worst_symbol["symbol"],
            "best_month_bucket": best_month["month_bucket"],
            "worst_month_bucket": worst_month["month_bucket"],
            "attribution_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_phase2_wider_reference_attribution_ready_for_failure_cluster_review",
        }
        interpretation = [
            "V1.34U attributes the current phase-2 wider reference after the mild-block refinement.",
            "The point is to identify where the current wider reference is genuinely earning its retained status and where any remaining drag is still concentrated.",
        ]
        return V134UCommercialAerospacePhase2WiderReferenceAttributionReport(
            summary=summary,
            tier_rows=tier_rows,
            symbol_rows=symbol_rows,
            month_rows=month_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UCommercialAerospacePhase2WiderReferenceAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UCommercialAerospacePhase2WiderReferenceAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134u_commercial_aerospace_phase2_wider_reference_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
