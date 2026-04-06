from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)
from a_share_quant.strategy.v124z_commercial_aerospace_control_surface_rolling_forward_audit_v1 import (
    V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer,
)


@dataclass(slots=True)
class V125CCommercialAerospaceControlSemanticsNarrowingScanReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V125CCommercialAerospaceControlSemanticsNarrowingScanAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _evaluate_variant(self, rows: list[dict[str, Any]], *, variant: str) -> dict[str, Any]:
        if variant == "base_reference":
            elig_fn = lambda r: r["eligibility_flag"]
            risk_fn = lambda r: r["de_risk_watch_flag"]
        elif variant == "primary_only_top2_proxy":
            elig_fn = lambda r: r["authority_semantic"] == "control_eligible_primary" and r["control_strength_score_rank_within_date"] <= 2
            risk_fn = lambda r: r["authority_semantic"] == "control_eligible_primary" and r["de_risk_watch_score_rank_desc_within_date"] <= 2
        elif variant == "primary_only_top3_proxy":
            elig_fn = lambda r: r["authority_semantic"] == "control_eligible_primary" and r["control_strength_score_rank_within_date"] <= 3
            risk_fn = lambda r: r["authority_semantic"] == "control_eligible_primary" and r["de_risk_watch_score_rank_desc_within_date"] <= 3
        elif variant == "primary_plus_support_highconviction":
            elig_fn = lambda r: (
                (r["authority_semantic"] == "control_eligible_primary" and r["control_strength_score_rank_within_date"] <= 3)
                or (r["authority_semantic"] == "control_eligible_support" and r["control_strength_score_rank_within_date"] == 1)
            )
            risk_fn = lambda r: (
                (r["authority_semantic"] == "control_eligible_primary" and r["de_risk_watch_score_rank_desc_within_date"] <= 2)
                or (r["authority_semantic"] == "control_eligible_support" and r["de_risk_watch_score_rank_desc_within_date"] == 1)
            )
        else:
            raise ValueError(variant)

        elig = [r["forward_return_10"] for r in rows if elig_fn(r)]
        non_elig = [r["forward_return_10"] for r in rows if not elig_fn(r)]
        risk = [r["forward_return_10"] for r in rows if risk_fn(r)]
        non_risk = [r["forward_return_10"] for r in rows if not risk_fn(r)]

        by_year: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_year.setdefault(row["trade_date"][:4], []).append(row)
        elig_year_spreads = []
        risk_year_spreads = []
        for year_rows in by_year.values():
            elig_y = [r["forward_return_10"] for r in year_rows if elig_fn(r)]
            non_elig_y = [r["forward_return_10"] for r in year_rows if not elig_fn(r)]
            risk_y = [r["forward_return_10"] for r in year_rows if risk_fn(r)]
            non_risk_y = [r["forward_return_10"] for r in year_rows if not risk_fn(r)]
            elig_year_spreads.append((sum(elig_y) / len(elig_y)) - (sum(non_elig_y) / len(non_elig_y)))
            risk_year_spreads.append((sum(non_risk_y) / len(non_risk_y)) - (sum(risk_y) / len(risk_y)))

        return {
            "variant": variant,
            "eligibility_forward_spread_10": round((sum(elig) / len(elig)) - (sum(non_elig) / len(non_elig)), 8),
            "de_risk_avoidance_spread_10": round((sum(non_risk) / len(non_risk)) - (sum(risk) / len(risk)), 8),
            "eligibility_year_spread_mean": round(sum(elig_year_spreads) / len(elig_year_spreads), 8),
            "eligibility_year_spread_min": round(min(elig_year_spreads), 8),
            "de_risk_year_spread_mean": round(sum(risk_year_spreads) / len(risk_year_spreads), 8),
            "de_risk_year_spread_min": round(min(risk_year_spreads), 8),
            "eligibility_flag_count": len(elig),
            "de_risk_flag_count": len(risk),
        }

    def analyze(self) -> V125CCommercialAerospaceControlSemanticsNarrowingScanReport:
        audit = V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer(self.repo_root).analyze()
        core = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(self.repo_root).analyze()
        authority_map = {row["symbol"]: row["authority_semantic"] for row in core.control_core_rows}

        rows = []
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in audit.audit_rows:
            enriched = {
                **row,
                "authority_semantic": authority_map[row["symbol"]],
            }
            rows.append(enriched)
            by_date.setdefault(row["trade_date"], []).append(enriched)

        for date_rows in by_date.values():
            control_sorted = sorted(date_rows, key=lambda r: r["control_strength_score"], reverse=True)
            risk_sorted = sorted(date_rows, key=lambda r: r["de_risk_watch_score"], reverse=True)
            for idx, row in enumerate(control_sorted, start=1):
                row["control_strength_score_rank_within_date"] = idx
            for idx, row in enumerate(risk_sorted, start=1):
                row["de_risk_watch_score_rank_desc_within_date"] = idx

        variants = [
            "base_reference",
            "primary_only_top2_proxy",
            "primary_only_top3_proxy",
            "primary_plus_support_highconviction",
        ]
        variant_rows = [self._evaluate_variant(rows, variant=v) for v in variants]
        best = max(variant_rows, key=lambda r: (r["eligibility_year_spread_mean"] + r["de_risk_year_spread_mean"]))

        summary = {
            "acceptance_posture": "freeze_v125c_commercial_aerospace_control_semantics_narrowing_scan_v1",
            "variant_count": len(variant_rows),
            "best_variant": best["variant"],
            "best_eligibility_year_spread_mean": best["eligibility_year_spread_mean"],
            "best_de_risk_year_spread_mean": best["de_risk_year_spread_mean"],
        }
        interpretation = [
            "V1.25C scans a few thinner control semantics instead of forcing replay on the first wide control surface.",
            "The purpose is to see whether a thinner primary-oriented definition restores chronological directionality.",
        ]
        return V125CCommercialAerospaceControlSemanticsNarrowingScanReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125CCommercialAerospaceControlSemanticsNarrowingScanReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125CCommercialAerospaceControlSemanticsNarrowingScanAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125c_commercial_aerospace_control_semantics_narrowing_scan_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
