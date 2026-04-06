from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)


CONTROL_FEATURES = [
    "trend_return_20",
    "elg_buy_sell_ratio_mean",
    "liquidity_amount_mean",
    "up_day_rate",
    "limit_heat_rate",
]
RISK_FEATURES = [
    "turnover_rate_f_mean",
    "volume_ratio_mean",
]


@dataclass(slots=True)
class V124WCommercialAerospaceControlExtractionReport:
    summary: dict[str, Any]
    eligibility_rows: list[dict[str, Any]]
    add_permission_rows: list[dict[str, Any]]
    de_risk_watch_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "eligibility_rows": self.eligibility_rows,
            "add_permission_rows": self.add_permission_rows,
            "de_risk_watch_rows": self.de_risk_watch_rows,
            "interpretation": self.interpretation,
        }


class V124WCommercialAerospaceControlExtractionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _z(self, rows: list[dict[str, Any]], key: str) -> dict[str, float]:
        mean = sum(row[key] for row in rows) / len(rows)
        var = sum((row[key] - mean) ** 2 for row in rows) / len(rows)
        std = math.sqrt(var) or 1.0
        return {row["symbol"]: (row[key] - mean) / std for row in rows}

    def analyze(self) -> V124WCommercialAerospaceControlExtractionReport:
        upstream = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(self.repo_root).analyze()
        rows = upstream.control_core_rows
        zmaps = {key: self._z(rows, key) for key in CONTROL_FEATURES + RISK_FEATURES}

        enriched: list[dict[str, Any]] = []
        for row in rows:
            symbol = row["symbol"]
            control_strength_score = (
                0.28 * zmaps["liquidity_amount_mean"][symbol]
                + 0.24 * zmaps["elg_buy_sell_ratio_mean"][symbol]
                + 0.20 * zmaps["trend_return_20"][symbol]
                + 0.16 * zmaps["up_day_rate"][symbol]
                + 0.12 * zmaps["limit_heat_rate"][symbol]
            )
            de_risk_watch_score = (
                0.30 * (-zmaps["trend_return_20"][symbol])
                + 0.25 * (-zmaps["elg_buy_sell_ratio_mean"][symbol])
                + 0.20 * zmaps["turnover_rate_f_mean"][symbol]
                + 0.15 * zmaps["volume_ratio_mean"][symbol]
                + 0.10 * (-zmaps["up_day_rate"][symbol])
            )
            enriched.append(
                {
                    **row,
                    "control_strength_score": round(control_strength_score, 6),
                    "de_risk_watch_score": round(de_risk_watch_score, 6),
                }
            )

        strength_sorted = sorted(enriched, key=lambda r: r["control_strength_score"], reverse=True)
        risk_sorted = sorted(enriched, key=lambda r: r["de_risk_watch_score"], reverse=True)

        eligibility_rows = []
        add_permission_rows = []
        de_risk_watch_rows = []
        for idx, row in enumerate(strength_sorted):
            if idx < 3:
                eligibility_rows.append({**row, "control_action": "eligibility_authority"})
            else:
                add_permission_rows.append({**row, "control_action": "add_permission_support"})

        risk_symbols = {row["symbol"] for row in risk_sorted[:4]}
        for row in enriched:
            if row["symbol"] in risk_symbols:
                de_risk_watch_rows.append({**row, "control_action": "de_risk_watch"})

        summary = {
            "acceptance_posture": "freeze_v124w_commercial_aerospace_control_extraction_v1",
            "control_core_count": len(rows),
            "eligibility_authority_count": len(eligibility_rows),
            "add_permission_support_count": len(add_permission_rows),
            "de_risk_watch_count": len(de_risk_watch_rows),
            "authoritative_rule": "commercial_aerospace_controls_must_be_extracted_from_the_thinned_formal_core_only",
            "recommended_next_posture": "audit_this_control_surface_before_any_replay",
        }
        interpretation = [
            "V1.24W is the first true commercial-aerospace control surface, extracted only from the thinned formal core.",
            "It does not yet authorize replay; it only names the initial eligibility, add-permission, and de-risk-watch layers.",
            "The next lawful step is to audit this control surface before binding it into replay.",
        ]
        return V124WCommercialAerospaceControlExtractionReport(
            summary=summary,
            eligibility_rows=eligibility_rows,
            add_permission_rows=add_permission_rows,
            de_risk_watch_rows=sorted(de_risk_watch_rows, key=lambda r: r["de_risk_watch_score"], reverse=True),
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124WCommercialAerospaceControlExtractionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124WCommercialAerospaceControlExtractionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124w_commercial_aerospace_control_extraction_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
