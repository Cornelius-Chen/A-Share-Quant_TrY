from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v123_1min_orthogonal_downside_utils import (
    POSITIVE_LABELS,
    balanced_accuracy,
    load_recent_1min_downside_rows,
)


@dataclass(slots=True)
class V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditReport:
        selection_path = self.repo_root / "reports" / "analysis" / "v123a_cpo_1min_orthogonal_downside_scan_v1.json"
        with selection_path.open("r", encoding="utf-8") as handle:
            selection_report = json.load(handle)
        score_name = selection_report["summary"]["chosen_score_name"]

        rows = load_recent_1min_downside_rows(self.repo_root)
        symbols = sorted({row["symbol"] for row in rows})
        symbol_rows: list[dict[str, Any]] = []
        scores: list[float] = []
        for holdout_symbol in symbols:
            train_rows = [row for row in rows if row["symbol"] != holdout_symbol]
            test_rows = [row for row in rows if row["symbol"] == holdout_symbol]
            if not train_rows or not test_rows:
                continue
            threshold = float(np.quantile([float(row[score_name]) for row in train_rows], 0.75))
            y_true = [row["proxy_action_label"] in POSITIVE_LABELS for row in test_rows]
            y_pred = [float(row[score_name]) >= threshold for row in test_rows]
            ba = balanced_accuracy(y_true, y_pred)
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
            "acceptance_posture": "freeze_v123c_cpo_1min_orthogonal_downside_symbol_holdout_audit_v1",
            "chosen_score_name": score_name,
            "symbol_count": len(symbol_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8) if scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(scores)), 8) if scores else 0.0,
            "recommended_next_posture": "three_agent_triage_chosen_orthogonal_1min_downside_branch",
        }
        interpretation = [
            "V1.23C tests whether the best orthogonal 1-minute downside branch survives symbol transfer.",
            "This is the final non-replay hurdle before adversarial triage.",
            "The next step is three-agent review.",
        ]
        return V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123c_cpo_1min_orthogonal_downside_symbol_holdout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

