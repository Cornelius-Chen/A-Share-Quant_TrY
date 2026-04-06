from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Report:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.quality_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_persistent_permission_quality_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_full_quality_add_archetype_audit_v1.csv"
        )

    def analyze(self) -> V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Report:
        with self.quality_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        for row in rows:
            for field in ("open_to_15m", "open_to_60m", "continuation_15_to_60m", "close_loc_15m", "burst_amount_share_15"):
                row[field] = float(row[field])

        threshold_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for close_loc_threshold in (0.60, 0.63, 0.65, 0.68, 0.70, 0.75):
            matched = [row for row in rows if row["close_loc_15m"] >= close_loc_threshold]
            full_hits = sum(1 for row in matched if row["quality_tier"] == "full_quality_persistent_permission")
            counterfactual_hits = len(matched) - full_hits
            precision = round(full_hits / len(matched), 8) if matched else 0.0
            coverage = round(full_hits / 5.0, 8)
            threshold_row = {
                "close_loc_15m_threshold": close_loc_threshold,
                "matched_count": len(matched),
                "full_quality_hit_count": full_hits,
                "counterfactual_hit_count": counterfactual_hits,
                "precision": precision,
                "coverage": coverage,
            }
            threshold_rows.append(threshold_row)
            if best_row is None or (
                threshold_row["precision"],
                threshold_row["coverage"],
                threshold_row["matched_count"],
            ) > (
                best_row["precision"],
                best_row["coverage"],
                best_row["matched_count"],
            ):
                best_row = threshold_row

        assert best_row is not None

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(threshold_rows[0].keys()))
            writer.writeheader()
            writer.writerows(threshold_rows)

        summary = {
            "acceptance_posture": "freeze_v134fj_commercial_aerospace_full_quality_add_archetype_audit_v1",
            "threshold_row_count": len(threshold_rows),
            "best_close_loc_15m_threshold": best_row["close_loc_15m_threshold"],
            "best_matched_count": best_row["matched_count"],
            "best_full_quality_hit_count": best_row["full_quality_hit_count"],
            "best_counterfactual_hit_count": best_row["counterfactual_hit_count"],
            "best_precision": best_row["precision"],
            "best_coverage": best_row["coverage"],
            "threshold_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "inside the persistent permission quality ladder, first-15m close location acts as the cleanest minimal archetype anchor for full-quality add behavior"
            ),
        }
        interpretation = [
            "V1.34FJ asks whether the strongest local add-permission tier can be summarized by a minimal archetype anchor.",
            "The aim is not to authorize execution, only to compress the strongest local tier into a readable supervision archetype.",
        ]
        return V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Report(
            summary=summary,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fj_commercial_aerospace_full_quality_add_archetype_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
