from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125i_commercial_aerospace_event_conditioned_control_surface_refresh_v1 import (
    V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer,
)
from a_share_quant.strategy.v125n_commercial_aerospace_structural_regime_discovery_v1 import (
    V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer,
)


@dataclass(slots=True)
class V125OCommercialAerospaceEventControlRegimeAuditReport:
    summary: dict[str, Any]
    regime_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "regime_rows": self.regime_rows,
            "interpretation": self.interpretation,
        }


class V125OCommercialAerospaceEventControlRegimeAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125OCommercialAerospaceEventControlRegimeAuditReport:
        regime_result = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(self.repo_root).analyze()
        regime_map = {row["trade_date"]: row["regime_semantic"] for row in regime_result.date_rows}

        control_upstream = V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer(self.repo_root)
        variant_rows, variant_audits, _meta = control_upstream._evaluate_variants()
        best_variant = variant_rows[0]["variant"]
        audited = variant_audits[best_variant]

        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in audited:
            semantic = regime_map.get(row["trade_date"])
            if semantic is None:
                continue
            grouped.setdefault(semantic, []).append(row)

        regime_rows: list[dict[str, Any]] = []
        for semantic, rows in grouped.items():
            elig = [r["forward_return_10"] for r in rows if r["eligibility_flag"]]
            non_elig = [r["forward_return_10"] for r in rows if not r["eligibility_flag"]]
            risk = [r["forward_return_10"] for r in rows if r["de_risk_watch_flag"]]
            non_risk = [r["forward_return_10"] for r in rows if not r["de_risk_watch_flag"]]
            regime_rows.append(
                {
                    "regime_semantic": semantic,
                    "row_count": len(rows),
                    "eligibility_flag_count": len(elig),
                    "de_risk_flag_count": len(risk),
                    "eligibility_forward_spread_10": round(
                        (sum(elig) / len(elig)) - (sum(non_elig) / len(non_elig)),
                        8,
                    )
                    if elig and non_elig
                    else 0.0,
                    "de_risk_avoidance_spread_10": round(
                        (sum(non_risk) / len(non_risk)) - (sum(risk) / len(risk)),
                        8,
                    )
                    if risk and non_risk
                    else 0.0,
                }
            )
        regime_rows.sort(key=lambda row: row["regime_semantic"])

        positive_eligibility_regimes = [
            row["regime_semantic"] for row in regime_rows if row["eligibility_forward_spread_10"] > 0
        ]
        negative_eligibility_regimes = [
            row["regime_semantic"] for row in regime_rows if row["eligibility_forward_spread_10"] < 0
        ]

        summary = {
            "acceptance_posture": "freeze_v125o_commercial_aerospace_event_control_regime_audit_v1",
            "best_variant": best_variant,
            "regime_count": len(regime_rows),
            "positive_eligibility_regimes": positive_eligibility_regimes,
            "negative_eligibility_regimes": negative_eligibility_regimes,
            "authoritative_rule": "commercial_aerospace_control_semantics_should_now_be_discussed_in_structure_regimes_not_calendar_years",
        }
        interpretation = [
            "V1.25O asks the question the right way: not whether 2024 or 2026 was good, but which machine-discovered structure regimes actually support lawful eligibility and de-risk semantics.",
            "This turns commercial aerospace chronology from calendar language into structural行情 language.",
        ]
        return V125OCommercialAerospaceEventControlRegimeAuditReport(
            summary=summary,
            regime_rows=regime_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125OCommercialAerospaceEventControlRegimeAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125OCommercialAerospaceEventControlRegimeAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125o_commercial_aerospace_event_control_regime_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
