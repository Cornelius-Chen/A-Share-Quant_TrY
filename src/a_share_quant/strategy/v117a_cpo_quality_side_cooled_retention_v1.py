from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V117ACpoQualitySideCooledRetentionReport:
    summary: dict[str, Any]
    retained_variant_row: dict[str, Any]
    equivalent_shadow_row: dict[str, Any]
    rejected_variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_variant_row": self.retained_variant_row,
            "equivalent_shadow_row": self.equivalent_shadow_row,
            "rejected_variant_rows": self.rejected_variant_rows,
            "interpretation": self.interpretation,
        }


class V117ACpoQualitySideCooledRetentionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116z_payload: dict[str, Any],
    ) -> V117ACpoQualitySideCooledRetentionReport:
        variant_map = {str(row["variant_name"]): dict(row) for row in list(v116z_payload.get("variant_rows", []))}
        retained = variant_map["cooled_q_0p25"]
        equivalent_shadow = variant_map["cooled_q_0p33"]
        rejected_rows = [
            variant_map["cooled_q_0p20"],
            variant_map["cooled_q_0p40"],
            variant_map["cooled_q_0p25_pc1_only"],
        ]

        summary = {
            "acceptance_posture": "freeze_v117a_cpo_quality_side_cooled_retention_v1",
            "candidate_posture": "quality_side_cooled_candidate_only",
            "retained_variant_name": "cooled_q_0p25",
            "equivalent_shadow_variant_name": "cooled_q_0p33",
            "effective_visible_axis": str(v116z_payload.get("summary", {}).get("effective_visible_axis")),
            "pc2_axis_active_any_variant": bool(v116z_payload.get("summary", {}).get("pc2_axis_active_any_variant")),
            "recommended_next_posture": "keep_q_0p25_as_quality_side_reference_and_stop_regrinding_quantiles_inside_same_family",
        }
        interpretation = [
            "V1.17A freezes the first quality-side cooled refinement pass instead of letting the project re-argue the same quantile family repeatedly.",
            "The retained quality-side reference remains q=0.25 because it dominates q=0.20 on coverage and equals q=0.33 on quality, while q=0.40 is clearly too hot.",
            "The family is now effectively PC1-driven at this stage; there is no evidence that a PC2-led quality-side refinement is adding real signal.",
        ]
        return V117ACpoQualitySideCooledRetentionReport(
            summary=summary,
            retained_variant_row=retained,
            equivalent_shadow_row=equivalent_shadow,
            rejected_variant_rows=rejected_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117ACpoQualitySideCooledRetentionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117ACpoQualitySideCooledRetentionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117a_cpo_quality_side_cooled_retention_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
