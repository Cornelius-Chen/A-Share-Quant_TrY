from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125i_commercial_aerospace_event_conditioned_control_surface_refresh_v1 import (
    V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer,
)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V125LCommercialAerospaceEventCoverageGapAuditReport:
    summary: dict[str, Any]
    year_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "year_rows": self.year_rows,
            "interpretation": self.interpretation,
        }


class V125LCommercialAerospaceEventCoverageGapAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_catalyst_event_registry_v1.csv"
        )

    def analyze(self) -> V125LCommercialAerospaceEventCoverageGapAuditReport:
        upstream = V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer(self.repo_root)
        variant_rows, variant_audits, _meta = upstream._evaluate_variants()
        best_variant = variant_rows[0]["variant"]
        audited = variant_audits[best_variant]
        registry_rows = [
            row
            for row in _load_csv(self.registry_path)
            if row["record_type"] == "historical_source" and row["public_release_time"]
        ]

        registry_by_year: dict[str, list[dict[str, str]]] = {}
        for row in registry_rows:
            registry_by_year.setdefault(row["public_release_time"][:4], []).append(row)

        audited_by_year: dict[str, list[dict[str, Any]]] = {}
        for row in audited:
            audited_by_year.setdefault(row["trade_date"][:4], []).append(row)

        years = sorted(set(registry_by_year) | set(audited_by_year))
        year_rows: list[dict[str, Any]] = []
        for year in years:
            reg_rows = registry_by_year.get(year, [])
            aud_rows = audited_by_year.get(year, [])
            event_day_count = len({row["public_release_time"][:10] for row in reg_rows})
            non_theme_event_day_count = len(
                {
                    row["public_release_time"][:10]
                    for row in reg_rows
                    if row["layer"] != "theme_heat"
                }
            )
            theme_heat_source_count = sum(1 for row in reg_rows if row["layer"] == "theme_heat")
            capital_supply_source_count = sum(
                1
                for row in reg_rows
                if row["layer"] in {"capital_mapping", "supply_chain_validation"}
            )
            eligibility_rows = [row for row in aud_rows if row["eligibility_flag"]]
            eligibility_day_count = len({row["trade_date"] for row in eligibility_rows})
            eligibility_forward = [row["forward_return_10"] for row in eligibility_rows]
            non_eligibility_forward = [row["forward_return_10"] for row in aud_rows if not row["eligibility_flag"]]
            eligibility_spread = (
                (sum(eligibility_forward) / len(eligibility_forward))
                - (sum(non_eligibility_forward) / len(non_eligibility_forward))
                if eligibility_forward and non_eligibility_forward
                else 0.0
            )
            year_rows.append(
                {
                    "year": year,
                    "historical_source_count": len(reg_rows),
                    "event_day_count": event_day_count,
                    "non_theme_event_day_count": non_theme_event_day_count,
                    "theme_heat_source_count": theme_heat_source_count,
                    "capital_supply_source_count": capital_supply_source_count,
                    "eligibility_flag_count": len(eligibility_rows),
                    "eligibility_day_count": eligibility_day_count,
                    "eligibility_forward_spread_10": round(eligibility_spread, 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v125l_commercial_aerospace_event_coverage_gap_audit_v1",
            "best_variant": best_variant,
            "zero_coverage_years": [row["year"] for row in year_rows if row["eligibility_flag_count"] == 0],
            "negative_tail_years": [
                row["year"] for row in year_rows if row["eligibility_flag_count"] > 0 and row["eligibility_forward_spread_10"] < 0
            ],
        }
        interpretation = [
            "V1.25L explains whether replay remains blocked because the event layer is absent, hype-dominated, or simply too sparse in a given year.",
            "This is the direct blocker audit after the first event-conditioned control rebuild looked alive on pooled statistics but still failed chronology tails.",
        ]
        return V125LCommercialAerospaceEventCoverageGapAuditReport(
            summary=summary,
            year_rows=year_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125LCommercialAerospaceEventCoverageGapAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125LCommercialAerospaceEventCoverageGapAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125l_commercial_aerospace_event_coverage_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
