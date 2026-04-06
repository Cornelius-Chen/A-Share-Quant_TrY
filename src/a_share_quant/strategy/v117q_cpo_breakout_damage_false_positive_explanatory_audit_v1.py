from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _reverse_candidate_score(row: dict[str, Any]) -> float:
    weakness_score = (
        -_to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("f60_high_time_ratio_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        - _to_float(row.get("f30_breakout_efficiency_rz"))
        - _to_float(row.get("f60_breakout_efficiency_rz"))
    )
    damage_score = (
        _to_float(row.get("f30_upper_shadow_ratio_rz"))
        + _to_float(row.get("f60_upper_shadow_ratio_rz"))
        + _to_float(row.get("f30_failed_push_proxy"))
        + _to_float(row.get("f60_failed_push_proxy"))
        + _to_float(row.get("d15_60_failed_push_proxy"))
    )
    return weakness_score + damage_score


def _shooting_star_trap_score(row: dict[str, Any]) -> float:
    return (
        _to_float(row.get("f30_upper_shadow_ratio_rz"))
        + _to_float(row.get("f60_upper_shadow_ratio_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        - _to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("f60_high_time_ratio_rz"))
    )


def _false_breakout_damage_score(row: dict[str, Any]) -> float:
    return (
        -_to_float(row.get("f30_breakout_efficiency_rz"))
        - _to_float(row.get("f60_breakout_efficiency_rz"))
        - _to_float(row.get("f30_pullback_from_high_rz"))
        - _to_float(row.get("f60_pullback_from_high_rz"))
        + _to_float(row.get("f30_failed_push_proxy"))
        + _to_float(row.get("f60_failed_push_proxy"))
    )


def _retail_chase_trap_score(row: dict[str, Any]) -> float:
    return (
        _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_last_bar_volume_share_rz"))
        + _to_float(row.get("f60_last_bar_volume_share_rz"))
        + _to_float(row.get("f30_close_location_rz"))
        + _to_float(row.get("f60_close_location_rz"))
    )


@dataclass(slots=True)
class V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditReport:
    summary: dict[str, Any]
    explanatory_rows: list[dict[str, Any]]
    flagged_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "explanatory_rows": self.explanatory_rows,
            "flagged_rows": self.flagged_rows,
            "interpretation": self.interpretation,
        }


class V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        rows_path: Path,
        v117o_payload: dict[str, Any],
    ) -> V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditReport:
        rows = _load_csv_rows(rows_path)
        base_map = {
            (str(row["signal_trade_date"]), str(row["symbol"]), str(row["action_context"])): dict(row)
            for row in rows
        }
        threshold = _to_float(v117o_payload["summary"]["best_threshold"])

        passing_rows: list[dict[str, Any]] = []
        for row in list(v117o_payload.get("external_pool_rows", [])):
            if str(row.get("action_context")) != "add_vs_hold":
                continue
            if _to_float(row.get("candidate_damage_score")) < threshold:
                continue
            key = (str(row["signal_trade_date"]), str(row["symbol"]), str(row["action_context"]))
            source_row = base_map[key]
            enriched = dict(row)
            enriched["reverse_candidate_score"] = round(_reverse_candidate_score(source_row), 6)
            enriched["shooting_star_trap_score"] = round(_shooting_star_trap_score(source_row), 6)
            enriched["false_breakout_damage_proxy_score"] = round(_false_breakout_damage_score(source_row), 6)
            enriched["retail_chase_trap_score"] = round(_retail_chase_trap_score(source_row), 6)
            passing_rows.append(enriched)

        true_positive_rows = [row for row in passing_rows if bool(row.get("positive_add_label"))]
        false_positive_rows = [row for row in passing_rows if not bool(row.get("positive_add_label"))]

        metric_names = (
            "reverse_candidate_score",
            "shooting_star_trap_score",
            "false_breakout_damage_proxy_score",
            "retail_chase_trap_score",
        )
        explanatory_rows: list[dict[str, Any]] = []
        for metric_name in metric_names:
            true_mean = (
                sum(_to_float(row.get(metric_name)) for row in true_positive_rows) / len(true_positive_rows)
                if true_positive_rows
                else 0.0
            )
            false_mean = (
                sum(_to_float(row.get(metric_name)) for row in false_positive_rows) / len(false_positive_rows)
                if false_positive_rows
                else 0.0
            )
            explanatory_rows.append(
                {
                    "metric_name": metric_name,
                    "true_positive_mean": round(true_mean, 6),
                    "false_positive_mean": round(false_mean, 6),
                    "false_minus_true_gap": round(false_mean - true_mean, 6),
                    "helps_explain_false_positives": false_mean > true_mean,
                }
            )
        explanatory_rows.sort(key=lambda row: row["false_minus_true_gap"], reverse=True)

        passing_rows.sort(
            key=lambda row: (
                bool(row.get("positive_add_label")),
                -_to_float(row.get("retail_chase_trap_score")),
                -_to_float(row.get("false_breakout_damage_proxy_score")),
            )
        )
        flagged_rows = [
            {
                "signal_trade_date": str(row["signal_trade_date"]),
                "symbol": str(row["symbol"]),
                "positive_add_label": bool(row["positive_add_label"]),
                "candidate_damage_score": _to_float(row["candidate_damage_score"]),
                "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                "reverse_candidate_score": _to_float(row.get("reverse_candidate_score")),
                "false_breakout_damage_proxy_score": _to_float(row.get("false_breakout_damage_proxy_score")),
                "retail_chase_trap_score": _to_float(row.get("retail_chase_trap_score")),
            }
            for row in passing_rows
        ]

        summary = {
            "acceptance_posture": "freeze_v117q_cpo_breakout_damage_false_positive_explanatory_audit_v1",
            "best_threshold": round(threshold, 6),
            "passing_add_row_count": len(passing_rows),
            "true_positive_pass_count": len(true_positive_rows),
            "false_positive_pass_count": len(false_positive_rows),
            "top_explanatory_metric": explanatory_rows[0]["metric_name"] if explanatory_rows else "",
            "secondary_explanatory_layer_useful": any(row["helps_explain_false_positives"] for row in explanatory_rows),
            "recommended_next_posture": "send_breakout_damage_external_audit_family_to_three_run_adversarial_review_and_keep_secondary_layers_explanatory_only",
        }
        interpretation = [
            "V1.17Q does not reopen the degraded reverse branch as a mainline. It checks whether reverse-signal and human-heuristic proxies help explain the breakout-damage false positives.",
            "Any value found here is explanatory only: it can justify later drawdown-control interactions, but it cannot hijack the positive-side mainline.",
            "This is the disciplined way to let human experience and reverse signals inform the project without letting them silently retake policy status.",
        ]
        return V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditReport(
            summary=summary,
            explanatory_rows=explanatory_rows,
            flagged_rows=flagged_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        v117o_payload=json.loads((repo_root / "reports" / "analysis" / "v117o_cpo_breakout_damage_external_pool_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117q_cpo_breakout_damage_false_positive_explanatory_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
