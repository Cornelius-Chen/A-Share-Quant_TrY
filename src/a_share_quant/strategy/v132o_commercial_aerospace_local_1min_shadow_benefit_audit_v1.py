from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V132OCommercialAerospaceLocal1MinShadowBenefitAuditReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "interpretation": self.interpretation,
        }


class V132OCommercialAerospaceLocal1MinShadowBenefitAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.rule_rows_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_rule_false_positive_rows_v1.csv"
        )
        self.supervision_rows_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_override_supervision_rows_v1.csv"
        )

    def analyze(self) -> V132OCommercialAerospaceLocal1MinShadowBenefitAuditReport:
        rule_rows = _load_csv_rows(self.rule_rows_path)
        supervision_rows = _load_csv_rows(self.supervision_rows_path)
        supervision_map = {
            (
                row["signal_trade_date"],
                row["execution_trade_date"],
                row["symbol"],
                row["action"],
            ): row
            for row in supervision_rows
        }

        enriched_rows: list[dict[str, Any]] = []
        for row in rule_rows:
            key = (
                row["signal_trade_date"],
                row["execution_trade_date"],
                row["symbol"],
                row["action"],
            )
            supervision = supervision_map[key]
            enriched_rows.append(
                {
                    "predicted_tier": row["predicted_tier"],
                    "notional": _to_float(supervision, "order_notional"),
                    "weight": _to_float(supervision, "weight_vs_initial_capital"),
                    "forward_return_10": _to_float(supervision, "forward_return_10"),
                    "max_adverse_return_10": _to_float(supervision, "max_adverse_return_10"),
                }
            )

        total_notional = sum(row["notional"] for row in enriched_rows)
        total_weight = sum(row["weight"] for row in enriched_rows)
        total_negative_forward_notional = sum(
            row["notional"] * max(0.0, -row["forward_return_10"]) for row in enriched_rows
        )
        total_adverse_notional = sum(
            row["notional"] * max(0.0, -row["max_adverse_return_10"]) for row in enriched_rows
        )

        flagged_rows = [row for row in enriched_rows if row["predicted_tier"] != "unmatched"]
        unflagged_rows = [row for row in enriched_rows if row["predicted_tier"] == "unmatched"]

        def _mean(rows: list[dict[str, Any]], key: str) -> float:
            if not rows:
                return 0.0
            return sum(float(row[key]) for row in rows) / len(rows)

        flagged_negative_forward_notional = sum(
            row["notional"] * max(0.0, -row["forward_return_10"]) for row in flagged_rows
        )
        flagged_adverse_notional = sum(
            row["notional"] * max(0.0, -row["max_adverse_return_10"]) for row in flagged_rows
        )

        tier_rows: list[dict[str, Any]] = []
        for tier in ("severe_override_positive", "reversal_watch", "mild_override_watch"):
            tier_subset = [row for row in flagged_rows if row["predicted_tier"] == tier]
            tier_notional = sum(row["notional"] for row in tier_subset)
            tier_negative_forward_notional = sum(
                row["notional"] * max(0.0, -row["forward_return_10"]) for row in tier_subset
            )
            tier_adverse_notional = sum(
                row["notional"] * max(0.0, -row["max_adverse_return_10"]) for row in tier_subset
            )
            tier_rows.append(
                {
                    "predicted_tier": tier,
                    "row_count": len(tier_subset),
                    "notional_share": round(tier_notional / total_notional, 8) if total_notional else 0.0,
                    "mean_forward_return_10": round(_mean(tier_subset, "forward_return_10"), 8),
                    "mean_max_adverse_return_10": round(_mean(tier_subset, "max_adverse_return_10"), 8),
                    "negative_forward_notional_share": (
                        round(tier_negative_forward_notional / total_negative_forward_notional, 8)
                        if total_negative_forward_notional
                        else 0.0
                    ),
                    "adverse_notional_share": (
                        round(tier_adverse_notional / total_adverse_notional, 8)
                        if total_adverse_notional
                        else 0.0
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v132o_commercial_aerospace_local_1min_shadow_benefit_audit_v1",
            "buy_execution_row_count": len(enriched_rows),
            "flagged_execution_count": len(flagged_rows),
            "flagged_execution_share": round(len(flagged_rows) / len(enriched_rows), 8) if enriched_rows else 0.0,
            "flagged_notional_share": round(sum(row["notional"] for row in flagged_rows) / total_notional, 8)
            if total_notional
            else 0.0,
            "flagged_weight_share": round(sum(row["weight"] for row in flagged_rows) / total_weight, 8)
            if total_weight
            else 0.0,
            "flagged_forward_return_10_mean": round(_mean(flagged_rows, "forward_return_10"), 8),
            "unflagged_forward_return_10_mean": round(_mean(unflagged_rows, "forward_return_10"), 8),
            "flagged_max_adverse_return_10_mean": round(_mean(flagged_rows, "max_adverse_return_10"), 8),
            "unflagged_max_adverse_return_10_mean": round(_mean(unflagged_rows, "max_adverse_return_10"), 8),
            "flagged_negative_forward_notional_share": (
                round(flagged_negative_forward_notional / total_negative_forward_notional, 8)
                if total_negative_forward_notional
                else 0.0
            ),
            "flagged_adverse_notional_share": (
                round(flagged_adverse_notional / total_adverse_notional, 8) if total_adverse_notional else 0.0
            ),
            "authoritative_rule": "the local 1min branch earns governance credibility when a small flagged slice of buy executions accounts for a disproportionate share of later downside notional without intruding into clean controls",
        }
        interpretation = [
            "V1.32O is a shadow-only benefit audit for the local 1-minute override rules on the frozen buy-execution surface.",
            "The goal is not replay promotion; it is to quantify whether the narrow minute governance layer concentrates on later bad notional rather than merely flagging many trades.",
        ]
        return V132OCommercialAerospaceLocal1MinShadowBenefitAuditReport(
            summary=summary,
            tier_rows=tier_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132OCommercialAerospaceLocal1MinShadowBenefitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132OCommercialAerospaceLocal1MinShadowBenefitAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132o_commercial_aerospace_local_1min_shadow_benefit_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
