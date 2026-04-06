from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_1min_label_plane_utils import load_recent_1min_labeled_rows
from a_share_quant.strategy.v122_supportive_continuation_utils import _zscore


def _balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [i for i, value in enumerate(y_true) if value]
    negatives = [i for i, value in enumerate(y_true) if not value]
    pos_recall = sum(y_pred[i] for i in positives) / len(positives) if positives else 0.0
    neg_recall = sum((not y_pred[i]) for i in negatives) / len(negatives) if negatives else 0.0
    return (pos_recall + neg_recall) / 2.0


@dataclass(slots=True)
class V122QCpo1MinDownsideFailureSymbolHoldoutAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V122QCpo1MinDownsideFailureSymbolHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_rows(self) -> list[dict[str, Any]]:
        rows = load_recent_1min_labeled_rows(self.repo_root)
        burst_z = _zscore([float(row["burst_then_fade_score"]) for row in rows])
        upper_shadow_z = _zscore([float(row["upper_shadow_pct"]) for row in rows])
        pullback_z = _zscore([float(row["micro_pullback_depth"]) for row in rows])
        push_z = _zscore([float(row["push_efficiency"]) for row in rows])
        late_z = _zscore([float(row["late_session_integrity_score"]) for row in rows])
        close_location_z = _zscore([float(row["close_location"]) for row in rows])
        reclaim_z = _zscore([float(row["reclaim_after_break_score"]) for row in rows])
        abs_close_vs_vwap_z = _zscore([abs(float(row["close_vs_vwap"])) for row in rows])
        for index, row in enumerate(rows):
            row["downside_failure_score"] = float(
                0.26 * burst_z[index]
                + 0.18 * upper_shadow_z[index]
                + 0.16 * pullback_z[index]
                - 0.14 * push_z[index]
                - 0.12 * late_z[index]
                - 0.08 * close_location_z[index]
                - 0.04 * reclaim_z[index]
                + 0.02 * abs_close_vs_vwap_z[index]
            )
        return rows

    def analyze(self) -> V122QCpo1MinDownsideFailureSymbolHoldoutAuditReport:
        rows = self._load_rows()
        symbols = sorted({row["symbol"] for row in rows})
        symbol_rows = []
        scores: list[float] = []
        for holdout_symbol in symbols:
            train_rows = [row for row in rows if row["symbol"] != holdout_symbol]
            test_rows = [row for row in rows if row["symbol"] == holdout_symbol]
            if not train_rows or not test_rows:
                continue
            threshold = float(np.quantile([row["downside_failure_score"] for row in train_rows], 0.75))
            y_true = [row["proxy_action_label"] in {"reduce_probe", "close_probe"} for row in test_rows]
            y_pred = [row["downside_failure_score"] >= threshold for row in test_rows]
            ba = _balanced_accuracy(y_true, y_pred)
            scores.append(ba)
            symbol_rows.append(
                {
                    "holdout_symbol": holdout_symbol,
                    "test_row_count": len(test_rows),
                    "threshold": round(threshold, 8),
                    "balanced_accuracy": round(ba, 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122q_cpo_1min_downside_failure_symbol_holdout_audit_v1",
            "symbol_count": len(symbol_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8) if scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(scores)), 8) if scores else 0.0,
            "recommended_next_posture": "triage_1min_downside_failure_branch",
        }
        interpretation = [
            "V1.22Q tests whether the new 1-minute downside failure score survives symbol holdout.",
            "If this branch survives both chronology and symbol transfer, it becomes the strongest recent 1-minute downside candidate.",
            "The next step is adversarial triage.",
        ]
        return V122QCpo1MinDownsideFailureSymbolHoldoutAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122QCpo1MinDownsideFailureSymbolHoldoutAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122QCpo1MinDownsideFailureSymbolHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122q_cpo_1min_downside_failure_symbol_holdout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
