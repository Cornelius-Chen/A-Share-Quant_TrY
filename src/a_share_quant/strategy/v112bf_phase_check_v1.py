from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BFPhaseCheckReport:
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


class V112BFPhaseCheckAnalyzer:
    def analyze(self, *, aggressive_pilot_payload: dict[str, Any]) -> V112BFPhaseCheckReport:
        summary_in = dict(aggressive_pilot_payload.get("summary", {}))
        if int(summary_in.get("trade_count", 0)) <= 0:
            raise ValueError("V1.12BF requires at least one no-leak aggressive trade.")
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BF phase check requires explicit no-leak enforcement.")

        summary = {
            "acceptance_posture": "keep_v112bf_as_cpo_aggressive_no_leak_black_box_portfolio_pilot",
            "do_open_v112bf_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "no_leak_enforced": True,
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bf_aggressive_pilot",
                "actual": {
                    "trade_count": summary_in.get("trade_count"),
                    "total_return": summary_in.get("total_return"),
                    "oracle_return_gap": summary_in.get("oracle_return_gap"),
                },
                "reading": "The pilot is only useful if it produces a real no-leak trade path and an explicit oracle gap.",
            }
        ]
        interpretation = [
            "V1.12BF is valid because it produces a no-leak aggressive portfolio trace rather than only a model score.",
        ]
        return V112BFPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bf_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BFPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
