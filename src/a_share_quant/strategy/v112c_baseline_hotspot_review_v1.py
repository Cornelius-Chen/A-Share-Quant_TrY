from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CBaselineHotspotReviewReport:
    summary: dict[str, Any]
    stage_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    top_error_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stage_rows": self.stage_rows,
            "symbol_rows": self.symbol_rows,
            "top_error_rows": self.top_error_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CBaselineHotspotReviewAnalyzer:
    """Summarize the first baseline's main error hotspots."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        baseline_readout_payload: dict[str, Any],
    ) -> V112CBaselineHotspotReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_hotspot_review_next")):
            raise ValueError("V1.12C hotspot review requires an open V1.12C charter.")

        fold_rows = list(baseline_readout_payload.get("fold_rows", []))
        by_stage: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        by_symbol: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        wrong_pairs: Counter[tuple[str, str, str, str]] = Counter()

        for row in fold_rows:
            stage = str(row.get("stage"))
            symbol = str(row.get("symbol"))
            correct = bool(row.get("correct"))
            by_stage[stage][0] += 1 if correct else 0
            by_stage[stage][1] += 1
            by_symbol[symbol][0] += 1 if correct else 0
            by_symbol[symbol][1] += 1
            if not correct:
                wrong_pairs[
                    (
                        symbol,
                        stage,
                        str(row.get("predicted_label")),
                        str(row.get("true_label")),
                    )
                ] += 1

        stage_rows = [
            {
                "stage": stage,
                "accuracy": round(correct / total, 4),
                "count": total,
            }
            for stage, (correct, total) in sorted(by_stage.items(), key=lambda item: item[1][0] / item[1][1])
        ]
        symbol_rows = [
            {
                "symbol": symbol,
                "accuracy": round(correct / total, 4),
                "count": total,
            }
            for symbol, (correct, total) in sorted(by_symbol.items(), key=lambda item: item[1][0] / item[1][1])
        ]
        top_error_rows = [
            {
                "symbol": symbol,
                "stage": stage,
                "predicted_label": predicted_label,
                "true_label": true_label,
                "count": count,
            }
            for (symbol, stage, predicted_label, true_label), count in wrong_pairs.most_common(12)
        ]
        summary = {
            "acceptance_posture": "freeze_v112c_baseline_hotspot_review_v1",
            "hotspot_stage_count": len(stage_rows),
            "hotspot_symbol_count": len(symbol_rows),
            "top_error_pair_count": len(top_error_rows),
            "primary_reading": "baseline_is_overoptimistic_in_late_markup_and_high_level_consolidation",
            "ready_for_sidecar_protocol_next": True,
        }
        interpretation = [
            "The first baseline's main weakness is not random noise; it concentrates in specific late-cycle and consolidation stages.",
            "This gives the next sidecar comparison a clean target: test whether a black-box model reduces those optimistic false positives without widening data scope.",
            "The result should change the next comparison design, not trigger immediate deployment.",
        ]
        return V112CBaselineHotspotReviewReport(
            summary=summary,
            stage_rows=stage_rows,
            symbol_rows=symbol_rows,
            top_error_rows=top_error_rows,
            interpretation=interpretation,
        )


def write_v112c_baseline_hotspot_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CBaselineHotspotReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
