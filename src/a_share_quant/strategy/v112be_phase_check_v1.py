from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BEPhaseCheckReport:
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


class V112BEPhaseCheckAnalyzer:
    def analyze(self, *, oracle_benchmark_payload: dict[str, Any]) -> V112BEPhaseCheckReport:
        summary_in = dict(oracle_benchmark_payload.get("summary", {}))
        trade_count = int(summary_in.get("trade_count", 0))
        equity_points = int(summary_in.get("equity_curve_point_count", 0))
        if trade_count <= 0:
            raise ValueError("V1.12BE requires at least one oracle trade.")
        if equity_points <= 0:
            raise ValueError("V1.12BE requires a non-empty equity curve.")

        summary = {
            "acceptance_posture": "keep_v112be_as_cpo_oracle_upper_bound_benchmark",
            "do_open_v112be_now": True,
            "trade_count": trade_count,
            "future_information_allowed": bool(summary_in.get("future_information_allowed")),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112be_oracle_benchmark",
                "actual": {
                    "trade_count": trade_count,
                    "total_return": summary_in.get("total_return"),
                    "max_drawdown": summary_in.get("max_drawdown"),
                },
                "reading": "The oracle benchmark is only useful if it produces a real hindsight upper-bound portfolio trace.",
            }
        ]
        interpretation = [
            "V1.12BE is valid because it produces an explicit hindsight upper-bound benchmark without opening no-leak training rights.",
        ]
        return V112BEPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112be_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BEPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
