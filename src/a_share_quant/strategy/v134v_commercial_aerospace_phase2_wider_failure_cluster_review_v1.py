from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134VCommercialAerospacePhase2WiderFailureClusterReviewReport:
    summary: dict[str, Any]
    cluster_rows: list[dict[str, Any]]
    failure_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cluster_rows": self.cluster_rows,
            "failure_rows": self.failure_rows,
            "interpretation": self.interpretation,
        }


class V134VCommercialAerospacePhase2WiderFailureClusterReviewAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_mild_block_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_wider_failure_cluster_review_v1.csv"
        )

    def analyze(self) -> V134VCommercialAerospacePhase2WiderFailureClusterReviewReport:
        with self.sessions_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            all_rows = list(csv.DictReader(handle))

        failure_rows = [
            row for row in all_rows
            if float(row["same_day_loss_avoided"]) < 0
        ]

        cluster_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in failure_rows:
            cluster_key = f"{row['predicted_tier']}|{row['month_bucket']}"
            cluster_buckets[cluster_key].append(row)

        cluster_rows = []
        for cluster_key, subset in sorted(cluster_buckets.items()):
            predicted_tier, month_bucket = cluster_key.split("|", 1)
            total_drag = sum(float(row["same_day_loss_avoided"]) for row in subset)
            cluster_rows.append(
                {
                    "cluster_key": cluster_key,
                    "predicted_tier": predicted_tier,
                    "month_bucket": month_bucket,
                    "failure_count": len(subset),
                    "total_same_day_loss_avoided_drag": round(total_drag, 4),
                    "worst_symbol": min(subset, key=lambda row: float(row["same_day_loss_avoided"]))["symbol"],
                }
            )
        cluster_rows.sort(key=lambda row: float(row["total_same_day_loss_avoided_drag"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if cluster_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(cluster_rows[0].keys()))
                writer.writeheader()
                writer.writerows(cluster_rows)

        top_cluster = cluster_rows[0] if cluster_rows else None
        summary = {
            "acceptance_posture": "freeze_v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1",
            "negative_session_count": len(failure_rows),
            "failure_cluster_count": len(cluster_rows),
            "top_failure_cluster": top_cluster["cluster_key"] if top_cluster else "",
            "top_failure_cluster_drag": top_cluster["total_same_day_loss_avoided_drag"] if top_cluster else 0.0,
            "failure_csv": str(self.output_csv.relative_to(self.repo_root)) if cluster_rows else "",
            "authoritative_output": "commercial_aerospace_phase2_wider_failure_cluster_review_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34V reviews whether the current wider phase-2 reference still fails in a diffuse way or in a few concentrated clusters.",
            "A concentrated failure map is healthier because it suggests the branch should keep supervising localized edge cases rather than retreat from the wider lane entirely.",
        ]
        return V134VCommercialAerospacePhase2WiderFailureClusterReviewReport(
            summary=summary,
            cluster_rows=cluster_rows,
            failure_rows=failure_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VCommercialAerospacePhase2WiderFailureClusterReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VCommercialAerospacePhase2WiderFailureClusterReviewAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
