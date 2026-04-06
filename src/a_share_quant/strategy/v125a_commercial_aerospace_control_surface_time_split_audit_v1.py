from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124z_commercial_aerospace_control_surface_rolling_forward_audit_v1 import (
    V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer,
)


@dataclass(slots=True)
class V125ACommercialAerospaceControlSurfaceTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V125ACommercialAerospaceControlSurfaceTimeSplitAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125ACommercialAerospaceControlSurfaceTimeSplitAuditReport:
        upstream = V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer(self.repo_root).analyze()
        rows = upstream.audit_rows
        by_year: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_year.setdefault(row["trade_date"][:4], []).append(row)

        split_rows: list[dict[str, Any]] = []
        elig_spreads = []
        risk_spreads = []
        for year, values in sorted(by_year.items()):
            elig = [r["forward_return_10"] for r in values if r["eligibility_flag"]]
            non_elig = [r["forward_return_10"] for r in values if not r["eligibility_flag"]]
            risk = [r["forward_return_10"] for r in values if r["de_risk_watch_flag"]]
            non_risk = [r["forward_return_10"] for r in values if not r["de_risk_watch_flag"]]
            elig_spread = (sum(elig) / len(elig)) - (sum(non_elig) / len(non_elig))
            risk_spread = (sum(non_risk) / len(non_risk)) - (sum(risk) / len(risk))
            elig_spreads.append(elig_spread)
            risk_spreads.append(risk_spread)
            split_rows.append(
                {
                    "year": year,
                    "eligibility_forward_spread_10": round(elig_spread, 8),
                    "de_risk_watch_avoidance_spread_10": round(risk_spread, 8),
                    "row_count": len(values),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v125a_commercial_aerospace_control_surface_time_split_audit_v1",
            "year_count": len(split_rows),
            "eligibility_spread_mean": round(sum(elig_spreads) / len(elig_spreads), 8),
            "eligibility_spread_min": round(min(elig_spreads), 8),
            "de_risk_avoidance_spread_mean": round(sum(risk_spreads) / len(risk_spreads), 8),
            "de_risk_avoidance_spread_min": round(min(risk_spreads), 8),
        }
        interpretation = [
            "V1.25A checks whether the commercial-aerospace control surface still makes sense once the rolling audit is split by year.",
            "This is the chronology check immediately before any first replay authorization.",
        ]
        return V125ACommercialAerospaceControlSurfaceTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125ACommercialAerospaceControlSurfaceTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125ACommercialAerospaceControlSurfaceTimeSplitAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125a_commercial_aerospace_control_surface_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
