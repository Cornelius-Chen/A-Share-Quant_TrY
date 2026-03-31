from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BIPhaseCheckReport:
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


class V112BIPhaseCheckAnalyzer:
    def analyze(self, *, ranker_pilot_payload: dict[str, Any]) -> V112BIPhaseCheckReport:
        summary_in = dict(ranker_pilot_payload.get("summary", {}))
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BI phase check requires explicit no-leak enforcement.")
        if int(summary_in.get("equity_curve_point_count", 0)) <= 0:
            raise ValueError("V1.12BI requires an explicit equity curve.")

        summary = {
            "acceptance_posture": "keep_v112bi_as_cpo_cross_sectional_ranker_pilot",
            "do_open_v112bi_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("cash_ratio", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bi_ranker_pilot",
                "actual": {
                    "total_return": summary_in.get("total_return"),
                    "aggressive_return_delta": summary_in.get("aggressive_return_delta"),
                    "neutral_return_delta": summary_in.get("neutral_return_delta"),
                },
                "reading": "The phase is only meaningful if the ranker produces a real bounded portfolio line and an explicit comparison against current classifier tracks.",
            }
        ]
        interpretation = [
            "V1.12BI is valid because it tests target-function alignment on the same lawful layer instead of adding a new uncontrolled objective.",
        ]
        return V112BIPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bi_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BIPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
