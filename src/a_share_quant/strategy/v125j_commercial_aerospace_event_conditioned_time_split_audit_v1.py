from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125i_commercial_aerospace_event_conditioned_control_surface_refresh_v1 import (
    V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer,
)


@dataclass(slots=True)
class V125JCommercialAerospaceEventConditionedTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V125JCommercialAerospaceEventConditionedTimeSplitAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125JCommercialAerospaceEventConditionedTimeSplitAuditReport:
        upstream = V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer(self.repo_root)
        variant_rows, variant_audits, _meta = upstream._evaluate_variants()
        best_variant = variant_rows[0]["variant"]
        audited = variant_audits[best_variant]

        by_year: dict[str, list[dict[str, Any]]] = {}
        for row in audited:
            by_year.setdefault(row["trade_date"][:4], []).append(row)

        split_rows: list[dict[str, Any]] = []
        eligibility_spreads: list[float] = []
        de_risk_spreads: list[float] = []
        for year, year_rows in sorted(by_year.items()):
            year_elig = [r["forward_return_10"] for r in year_rows if r["eligibility_flag"]]
            year_non_elig = [r["forward_return_10"] for r in year_rows if not r["eligibility_flag"]]
            eligibility_spread = (
                (sum(year_elig) / len(year_elig)) - (sum(year_non_elig) / len(year_non_elig))
                if year_elig and year_non_elig
                else 0.0
            )
            year_risk = [r["forward_return_10"] for r in year_rows if r["de_risk_watch_flag"]]
            year_non_risk = [r["forward_return_10"] for r in year_rows if not r["de_risk_watch_flag"]]
            de_risk_spread = (
                (sum(year_non_risk) / len(year_non_risk)) - (sum(year_risk) / len(year_risk))
                if year_risk and year_non_risk
                else 0.0
            )
            if year_elig and year_non_elig:
                eligibility_spreads.append(eligibility_spread)
            if year_risk and year_non_risk:
                de_risk_spreads.append(de_risk_spread)
            split_rows.append(
                {
                    "year": year,
                    "eligibility_forward_spread_10": round(eligibility_spread, 8),
                    "de_risk_watch_avoidance_spread_10": round(de_risk_spread, 8),
                    "eligibility_flag_count": len(year_elig),
                    "de_risk_flag_count": len(year_risk),
                    "row_count": len(year_rows),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v125j_commercial_aerospace_event_conditioned_time_split_audit_v1",
            "best_variant": best_variant,
            "year_count": len(split_rows),
            "eligibility_spread_mean": round(sum(eligibility_spreads) / len(eligibility_spreads), 8)
            if eligibility_spreads
            else 0.0,
            "eligibility_spread_min": round(min(eligibility_spreads), 8) if eligibility_spreads else 0.0,
            "de_risk_avoidance_spread_mean": round(sum(de_risk_spreads) / len(de_risk_spreads), 8)
            if de_risk_spreads
            else 0.0,
            "de_risk_avoidance_spread_min": round(min(de_risk_spreads), 8) if de_risk_spreads else 0.0,
        }
        interpretation = [
            "V1.25J re-audits chronology after the event-conditioned control rebuild and keeps the winner on a year-by-year basis.",
            "Commercial aerospace remains replay-blocked unless both eligibility and de-risk semantics stop going negative in the worst split.",
        ]
        return V125JCommercialAerospaceEventConditionedTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125JCommercialAerospaceEventConditionedTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125JCommercialAerospaceEventConditionedTimeSplitAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125j_commercial_aerospace_event_conditioned_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
