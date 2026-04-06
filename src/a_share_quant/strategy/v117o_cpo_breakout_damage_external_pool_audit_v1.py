from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POSITIVE_FEATURES = (
    "f30_breakout_efficiency_rz",
    "f60_breakout_efficiency_rz",
    "f30_last_bar_return_rz",
    "f60_last_bar_return_rz",
    "f30_pullback_from_high_rz",
    "f60_pullback_from_high_rz",
)
NEGATIVE_FEATURES = (
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "d5_30_last_bar_upper_shadow_ratio_rz",
    "d15_60_last_bar_upper_shadow_ratio_rz",
    "f30_failed_push_proxy",
    "f60_failed_push_proxy",
    "d15_60_failed_push_proxy",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _candidate_damage_score(row: dict[str, Any]) -> float:
    positive_score = sum(_to_float(row.get(feature)) for feature in POSITIVE_FEATURES)
    negative_score = sum(_to_float(row.get(feature)) for feature in NEGATIVE_FEATURES)
    return positive_score - negative_score


def _is_positive_add_row(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


@dataclass(slots=True)
class V117OCpoBreakoutDamageExternalPoolAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    external_pool_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "external_pool_rows": self.external_pool_rows,
            "interpretation": self.interpretation,
        }


class V117OCpoBreakoutDamageExternalPoolAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V117OCpoBreakoutDamageExternalPoolAuditReport:
        rows = _load_csv_rows(rows_path)
        relevant_rows = [
            dict(row)
            for row in rows
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) in {"add_vs_hold", "entry_vs_skip"}
        ]
        add_rows = [row for row in relevant_rows if str(row.get("action_context")) == "add_vs_hold"]
        entry_rows = [row for row in relevant_rows if str(row.get("action_context")) == "entry_vs_skip"]
        positive_add_rows = [row for row in add_rows if _is_positive_add_row(row)]
        negative_add_rows = [row for row in add_rows if row not in positive_add_rows]

        for row in relevant_rows:
            row["candidate_damage_score"] = round(_candidate_damage_score(row), 6)
            row["positive_add_label"] = _is_positive_add_row(row)

        thresholds = sorted({_to_float(row["candidate_damage_score"]) for row in add_rows}, reverse=True)
        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positive_add_rows if _to_float(row["candidate_damage_score"]) >= threshold)
            fn = len(positive_add_rows) - tp
            fp = sum(1 for row in negative_add_rows if _to_float(row["candidate_damage_score"]) >= threshold)
            tn = len(negative_add_rows) - fp
            tpr = tp / len(positive_add_rows) if positive_add_rows else 0.0
            tnr = tn / len(negative_add_rows) if negative_add_rows else 0.0
            leakage_rate = (
                sum(1 for row in entry_rows if _to_float(row["candidate_damage_score"]) >= threshold) / len(entry_rows)
                if entry_rows
                else 0.0
            )
            balanced_accuracy = (tpr + tnr) / 2.0
            record = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_add_recall": round(tpr, 6),
                "negative_add_reject_rate": round(tnr, 6),
                "entry_leakage_rate": round(leakage_rate, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
            }
            threshold_audit_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        positive_mean = (
            sum(_to_float(row["candidate_damage_score"]) for row in positive_add_rows) / len(positive_add_rows)
            if positive_add_rows
            else 0.0
        )
        negative_mean = (
            sum(_to_float(row["candidate_damage_score"]) for row in negative_add_rows) / len(negative_add_rows)
            if negative_add_rows
            else 0.0
        )

        relevant_rows.sort(
            key=lambda row: (
                str(row["action_context"]) != "add_vs_hold",
                not bool(row["positive_add_label"]),
                -_to_float(row["candidate_damage_score"]),
            )
        )
        external_pool_rows = [
            {
                "signal_trade_date": str(row["signal_trade_date"]),
                "symbol": str(row["symbol"]),
                "action_context": str(row["action_context"]),
                "board_phase": str(row["board_phase"]),
                "candidate_damage_score": round(_to_float(row["candidate_damage_score"]), 6),
                "positive_add_label": bool(row["positive_add_label"]),
                "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
            }
            for row in relevant_rows
        ]

        summary = {
            "acceptance_posture": "freeze_v117o_cpo_breakout_damage_external_pool_audit_v1",
            "candidate_discriminator_name": "breakout_damage_containment_score_candidate",
            "external_pool_row_count": len(relevant_rows),
            "add_row_count": len(add_rows),
            "positive_add_row_count": len(positive_add_rows),
            "negative_add_row_count": len(negative_add_rows),
            "entry_row_count": len(entry_rows),
            "positive_vs_negative_add_gap": round(positive_mean - negative_mean, 6),
            "external_pool_signal_clear": positive_mean > negative_mean,
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "best_threshold_entry_leakage_rate": best_row["entry_leakage_rate"] if best_row else 0.0,
            "recommended_next_posture": "time_split_validate_breakout_damage_on_broader_add_pool_before_any_replay_facing_use",
        }
        interpretation = [
            "V1.17O moves the breakout-damage branch off the tiny retained family and onto a broader add-vs-hold external pool.",
            "It still treats entry rows only as leakage checks, not as training targets for the add discriminator.",
            "This keeps the branch aligned with held-position add semantics while finally testing it on a wider and dirtier surface.",
        ]
        return V117OCpoBreakoutDamageExternalPoolAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            external_pool_rows=external_pool_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117OCpoBreakoutDamageExternalPoolAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117OCpoBreakoutDamageExternalPoolAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117o_cpo_breakout_damage_external_pool_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
