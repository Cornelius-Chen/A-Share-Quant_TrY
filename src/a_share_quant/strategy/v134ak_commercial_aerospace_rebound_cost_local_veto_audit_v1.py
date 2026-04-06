from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Report:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    matched_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "matched_rows": self.matched_rows,
            "interpretation": self.interpretation,
        }


class V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.confirmation_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_volume_price_confirmation_audit_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_rebound_cost_local_veto_audit_v1.csv"
        )

    def _load_rows(self) -> list[dict[str, Any]]:
        with self.confirmation_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Report:
        rows = self._load_rows()
        threshold_rows: list[dict[str, Any]] = []

        for up_share_threshold in (0.45, 0.50, 0.55):
            for open_burst_floor in (-0.02, -0.01, 0.0):
                matched = [
                    row
                    for row in rows
                    if float(row["post_reversal_up_amount_share"]) >= up_share_threshold
                    and float(row["open_burst_return_5m"]) >= open_burst_floor
                ]
                rebound_hits = sum(1 for row in matched if row["regime_label"] == "rebound_cost_case")
                follow_hits = sum(1 for row in matched if row["regime_label"] == "followthrough_benefit_case")
                threshold_rows.append(
                    {
                        "up_share_threshold": up_share_threshold,
                        "open_burst_floor": open_burst_floor,
                        "matched_count": len(matched),
                        "rebound_cost_hit_count": rebound_hits,
                        "followthrough_hit_count": follow_hits,
                        "precision_rebound": round(rebound_hits / len(matched), 6) if matched else 0.0,
                        "rebound_coverage": round(
                            rebound_hits / sum(1 for row in rows if row["regime_label"] == "rebound_cost_case"),
                            6,
                        ),
                    }
                )

        best_row = max(
            threshold_rows,
            key=lambda row: (row["precision_rebound"], row["rebound_coverage"], -row["matched_count"]),
        )
        matched_rows = [
            row
            for row in rows
            if float(row["post_reversal_up_amount_share"]) >= best_row["up_share_threshold"]
            and float(row["open_burst_return_5m"]) >= best_row["open_burst_floor"]
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(threshold_rows[0].keys()))
            writer.writeheader()
            writer.writerows(threshold_rows)

        summary = {
            "acceptance_posture": "freeze_v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1",
            "best_up_share_threshold": best_row["up_share_threshold"],
            "best_open_burst_floor": best_row["open_burst_floor"],
            "best_matched_count": best_row["matched_count"],
            "best_rebound_cost_hit_count": best_row["rebound_cost_hit_count"],
            "best_followthrough_hit_count": best_row["followthrough_hit_count"],
            "best_precision_rebound": best_row["precision_rebound"],
            "best_rebound_coverage": best_row["rebound_coverage"],
            "threshold_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_rebound_cost_local_veto_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AK tries a very narrow local veto shape for rebound-cost reversal sessions.",
            "The goal is not global rule replacement; it is to see whether a small volume-price conjunction can catch a subset of rebound-cost cases without swallowing too many follow-through cases.",
        ]
        return V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Report(
            summary=summary,
            threshold_rows=threshold_rows,
            matched_rows=matched_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AKCommercialAerospaceReboundCostLocalVetoAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
