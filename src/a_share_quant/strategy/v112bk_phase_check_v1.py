from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BKPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BKPhaseCheckAnalyzer:
    def analyze(self, *, tree_ranker_search_payload: dict[str, Any]) -> V112BKPhaseCheckReport:
        summary_in = dict(tree_ranker_search_payload.get("summary", {}))
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BK phase check requires explicit no-leak enforcement.")
        if int(summary_in.get("equity_curve_point_count", 0)) <= 0:
            raise ValueError("V1.12BK requires an explicit equity curve.")
        if int(summary_in.get("variant_count", 0)) <= 0:
            raise ValueError("V1.12BK requires at least one evaluated tree/ranker variant.")

        summary = {
            "acceptance_posture": "keep_v112bk_as_cpo_tree_ranker_search_track",
            "do_open_v112bk_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("best_variant_cash_ratio", 0.0)),
            "best_variant_name": summary_in.get("best_variant_name"),
            "best_variant_total_return": float(summary_in.get("best_variant_total_return", 0.0)),
            "best_variant_max_drawdown": float(summary_in.get("best_variant_max_drawdown", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bk_tree_ranker_search",
                "actual": {
                    "best_variant_name": summary_in.get("best_variant_name"),
                    "best_variant_total_return": summary_in.get("best_variant_total_return"),
                    "best_variant_max_drawdown": summary_in.get("best_variant_max_drawdown"),
                    "beats_neutral_without_material_drawdown_worsening": summary_in.get(
                        "beats_neutral_without_material_drawdown_worsening"
                    ),
                },
                "reading": (
                    "The phase is only meaningful if the bounded tree/ranker search remains lawful, "
                    "returns a report-only benchmark, and preserves the neutral-baseline comparison."
                ),
            }
        ]
        interpretation = [
            "V1.12BK is valid because it searches a cheap tree/ranker zoo on the lawful CPO layer without opening formal training.",
        ]
        return V112BKPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bk_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BKPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
