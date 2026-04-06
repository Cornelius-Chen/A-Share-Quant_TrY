from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_supportive_continuation_utils import load_supportive_continuation_rows
from a_share_quant.strategy.v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery_v1 import _zscore


@dataclass(slots=True)
class V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


def _balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [i for i, value in enumerate(y_true) if value]
    negatives = [i for i, value in enumerate(y_true) if not value]
    pos_recall = sum(y_pred[i] for i in positives) / len(positives) if positives else 0.0
    neg_recall = sum((not y_pred[i]) for i in negatives) / len(negatives) if negatives else 0.0
    return (pos_recall + neg_recall) / 2.0


class V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_rows(self) -> list[dict[str, Any]]:
        supportive_rows = load_supportive_continuation_rows(self.repo_root)
        label_path = self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
        with label_path.open("r", encoding="utf-8") as handle:
            label_rows = list(csv.DictReader(handle))
        label_map = {
            (row["symbol"], row["trade_date"], row["clock_time"]): row["proxy_action_label"]
            for row in label_rows
        }
        rows = []
        for row in supportive_rows:
            label = label_map.get((row["symbol"], row["trade_date"], row["clock_time"]))
            if label not in {"add_probe", "reduce_probe"}:
                continue
            rows.append({**row, "proxy_action_label": label})

        push_z = _zscore([row["push_efficiency"] for row in rows])
        late_z = _zscore([row["late_session_integrity_score"] for row in rows])
        reclaim_z = _zscore([row["reclaim_after_break_score"] for row in rows])
        close_loc_z = _zscore([row["close_location"] for row in rows])
        close_vs_vwap_abs_z = _zscore([abs(row["close_vs_vwap"]) for row in rows])
        upper_shadow_z = _zscore([row["upper_shadow_pct"] for row in rows])
        pullback_z = _zscore([row["micro_pullback_depth"] for row in rows])
        burst_z = _zscore([row["burst_then_fade_score"] for row in rows])

        for index, row in enumerate(rows):
            row["add_reduce_separation_score"] = float(
                0.28 * push_z[index]
                + 0.24 * late_z[index]
                + 0.18 * reclaim_z[index]
                + 0.10 * close_loc_z[index]
                - 0.08 * close_vs_vwap_abs_z[index]
                - 0.05 * upper_shadow_z[index]
                - 0.04 * pullback_z[index]
                - 0.03 * burst_z[index]
            )
        return rows

    def analyze(self) -> V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditReport:
        rows = self._load_rows()
        unique_dates = sorted({row["trade_date"] for row in rows})
        split_rows = []
        test_scores: list[float] = []
        for split_index in range(1, len(unique_dates)):
            train_dates = set(unique_dates[:split_index])
            test_dates = set(unique_dates[split_index:])
            train_rows = [row for row in rows if row["trade_date"] in train_dates]
            test_rows = [row for row in rows if row["trade_date"] in test_dates]
            if not train_rows or not test_rows:
                continue
            threshold = float(np.quantile([row["add_reduce_separation_score"] for row in train_rows], 0.75))
            y_true = [row["proxy_action_label"] == "add_probe" for row in test_rows]
            y_pred = [row["add_reduce_separation_score"] >= threshold for row in test_rows]
            ba = _balanced_accuracy(y_true, y_pred)
            test_scores.append(ba)
            split_rows.append(
                {
                    "train_end_date": max(train_dates),
                    "test_start_date": min(test_dates),
                    "test_row_count": len(test_rows),
                    "threshold": round(threshold, 8),
                    "balanced_accuracy": round(ba, 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122m_cpo_1min_supportive_add_vs_reduce_time_split_audit_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(test_scores)), 8) if test_scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(test_scores)), 8) if test_scores else 0.0,
            "recommended_next_posture": "triage_supportive_add_vs_reduce_separation_score",
        }
        interpretation = [
            "V1.22M tests whether the supportive-family add-vs-reduce separation score survives date split.",
            "This is the minimum chronology audit needed before deciding whether the supportive family is moving toward a real add rule.",
            "The next step is triage, not replay.",
        ]
        return V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122m_cpo_1min_supportive_add_vs_reduce_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
