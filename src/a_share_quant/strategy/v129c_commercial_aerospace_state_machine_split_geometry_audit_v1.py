from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128y_commercial_aerospace_state_machine_supervised_table_v1 import (
    V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer,
)


TARGET_LABELS = ["probe", "full_pre", "full", "de_risk", "neutral_hold"]
SPLIT_RATIOS = [0.80, 0.85, 0.88, 0.90, 0.92, 0.95]


@dataclass(slots=True)
class V129CCommercialAerospaceStateMachineSplitGeometryAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V129CCommercialAerospaceStateMachineSplitGeometryAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _split_counters(self, rows: list[dict[str, Any]], ratio: float) -> dict[str, Any]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * ratio))
        train_dates = set(ordered_dates[:split_idx])
        test_dates = set(ordered_dates[split_idx:])
        train_counter = Counter(row["supervised_action_state"] for row in rows if row["trade_date"] in train_dates)
        test_counter = Counter(row["supervised_action_state"] for row in rows if row["trade_date"] in test_dates)

        train_high = train_counter["full_pre"] + train_counter["full"]
        test_high = test_counter["full_pre"] + test_counter["full"]
        supports_both_high = train_high > 0 and test_high > 0
        supports_full_pre_both = train_counter["full_pre"] > 0 and test_counter["full_pre"] > 0
        supports_full_both = train_counter["full"] > 0 and test_counter["full"] > 0
        supports_joint_full_pre_and_full_both = supports_full_pre_both and supports_full_both

        return {
            "split_ratio": ratio,
            "train_date_start": min(train_dates) if train_dates else "",
            "train_date_end": max(train_dates) if train_dates else "",
            "test_date_start": min(test_dates) if test_dates else "",
            "test_date_end": max(test_dates) if test_dates else "",
            "train_counts": {label: int(train_counter.get(label, 0)) for label in TARGET_LABELS},
            "test_counts": {label: int(test_counter.get(label, 0)) for label in TARGET_LABELS},
            "train_high_intensity_count": int(train_high),
            "test_high_intensity_count": int(test_high),
            "supports_high_intensity_both_sides": supports_both_high,
            "supports_full_pre_both_sides": supports_full_pre_both,
            "supports_full_both_sides": supports_full_both,
            "supports_joint_full_pre_and_full_both_sides": supports_joint_full_pre_and_full_both,
        }

    def analyze(self) -> V129CCommercialAerospaceStateMachineSplitGeometryAuditReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        split_rows = [self._split_counters(rows, ratio) for ratio in SPLIT_RATIOS]

        high_supported = [row for row in split_rows if row["supports_high_intensity_both_sides"]]
        full_pre_supported = [row for row in split_rows if row["supports_full_pre_both_sides"]]
        full_supported = [row for row in split_rows if row["supports_full_both_sides"]]
        joint_supported = [row for row in split_rows if row["supports_joint_full_pre_and_full_both_sides"]]

        summary = {
            "acceptance_posture": "freeze_v129c_commercial_aerospace_state_machine_split_geometry_audit_v1",
            "row_count": len(rows),
            "split_count": len(split_rows),
            "high_intensity_supported_split_ratios": [row["split_ratio"] for row in high_supported],
            "full_pre_supported_split_ratios": [row["split_ratio"] for row in full_pre_supported],
            "full_supported_split_ratios": [row["split_ratio"] for row in full_supported],
            "joint_full_pre_and_full_supported_split_ratios": [row["split_ratio"] for row in joint_supported],
            "best_high_intensity_support_ratio": high_supported[0]["split_ratio"] if high_supported else None,
            "authoritative_status": (
                "single_split_joint_support_unavailable"
                if not joint_supported
                else "single_split_joint_support_available"
            ),
            "authoritative_rule": "if no single lawful chronology split supports both full_pre and full on both sides, model improvement should shift from classifier tuning to split geometry / walk-forward redesign",
        }
        interpretation = [
            "V1.29C checks whether the current commercial-aerospace state machine failure is a classifier problem or a chronology support problem.",
            "The key question is not whether some ratio can support a combined high-intensity bucket, but whether one lawful split can support both full_pre and full on both train and test.",
        ]
        return V129CCommercialAerospaceStateMachineSplitGeometryAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129CCommercialAerospaceStateMachineSplitGeometryAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129CCommercialAerospaceStateMachineSplitGeometryAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129c_commercial_aerospace_state_machine_split_geometry_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
