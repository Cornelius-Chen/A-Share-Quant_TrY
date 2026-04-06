from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134NCommercialAerospaceBroaderHitSimulatorAttributionReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V134NCommercialAerospaceBroaderHitSimulatorAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_broader_hit_simulator_attribution_v1.csv"
        )

    def analyze(self) -> V134NCommercialAerospaceBroaderHitSimulatorAttributionReport:
        with self.sessions_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        tier_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        symbol_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            tier_buckets[row["predicted_tier"]].append(row)
            symbol_buckets[row["symbol"]].append(row)

        total_avoided = sum(float(row["same_day_loss_avoided"]) for row in rows)

        tier_rows = []
        for tier, subset in sorted(tier_buckets.items()):
            same_day_loss_avoided = sum(float(row["same_day_loss_avoided"]) for row in subset)
            tier_rows.append(
                {
                    "predicted_tier": tier,
                    "session_count": len(subset),
                    "mean_same_day_loss_avoided": round(same_day_loss_avoided / len(subset), 4),
                    "same_day_loss_avoided_total": round(same_day_loss_avoided, 4),
                    "same_day_loss_avoided_share": round(same_day_loss_avoided / total_avoided, 8) if total_avoided else 0.0,
                    "positive_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) > 0),
                    "negative_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) < 0),
                }
            )

        symbol_rows = []
        for symbol, subset in sorted(symbol_buckets.items()):
            same_day_loss_avoided = sum(float(row["same_day_loss_avoided"]) for row in subset)
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "session_count": len(subset),
                    "same_day_loss_avoided_total": round(same_day_loss_avoided, 4),
                    "same_day_loss_avoided_share": round(same_day_loss_avoided / total_avoided, 8) if total_avoided else 0.0,
                    "positive_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) > 0),
                    "negative_session_count": sum(1 for row in subset if float(row["same_day_loss_avoided"]) < 0),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(tier_rows[0].keys()))
            writer.writeheader()
            writer.writerows(tier_rows)

        best_tier = max(tier_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        worst_tier = min(tier_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        best_symbol = max(symbol_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))
        worst_symbol = min(symbol_rows, key=lambda row: float(row["same_day_loss_avoided_total"]))

        summary = {
            "acceptance_posture": "freeze_v134n_commercial_aerospace_broader_hit_simulator_attribution_v1",
            "session_count": len(rows),
            "same_day_loss_avoided_total": round(total_avoided, 4),
            "best_tier": best_tier["predicted_tier"],
            "worst_tier": worst_tier["predicted_tier"],
            "best_symbol": best_symbol["symbol"],
            "worst_symbol": worst_symbol["symbol"],
            "attribution_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_hit_simulator_attribution_ready_for_supervision_failure_review",
        }
        interpretation = [
            "V1.34N attributes the first broader-hit phase-2 simulator by predicted tier and symbol.",
            "The point is not replay promotion; it is to supervise whether the guarded widening remains directionally sensible and where the newly introduced drag lives.",
        ]
        return V134NCommercialAerospaceBroaderHitSimulatorAttributionReport(
            summary=summary,
            tier_rows=tier_rows,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134NCommercialAerospaceBroaderHitSimulatorAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NCommercialAerospaceBroaderHitSimulatorAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134n_commercial_aerospace_broader_hit_simulator_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
