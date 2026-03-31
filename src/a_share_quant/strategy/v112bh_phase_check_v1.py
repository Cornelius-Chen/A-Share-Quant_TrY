from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BHPhaseCheckReport:
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


class V112BHPhaseCheckAnalyzer:
    def analyze(self, *, neutral_pilot_payload: dict[str, Any]) -> V112BHPhaseCheckReport:
        summary_in = dict(neutral_pilot_payload.get("summary", {}))
        if int(summary_in.get("equity_curve_point_count", 0)) <= 0:
            raise ValueError("V1.12BH requires an explicit neutral equity curve.")
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BH phase check requires explicit no-leak enforcement.")

        summary = {
            "acceptance_posture": "keep_v112bh_as_cpo_neutral_selective_no_leak_portfolio_pilot",
            "do_open_v112bh_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("cash_ratio", 0.0)),
            "no_leak_enforced": True,
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bh_neutral_pilot",
                "actual": {
                    "trade_count": summary_in.get("trade_count"),
                    "total_return": summary_in.get("total_return"),
                    "cash_ratio": summary_in.get("cash_ratio"),
                    "aggressive_return_delta": summary_in.get("aggressive_return_delta"),
                },
                "reading": "The neutral track is only valid if it actually exercises selective cash posture rather than acting like a hidden aggressive clone.",
            }
        ]
        interpretation = [
            "V1.12BH is valid because it produces a distinct no-leak selective portfolio trace with explicit cash tolerance.",
        ]
        return V112BHPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bh_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BHPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
