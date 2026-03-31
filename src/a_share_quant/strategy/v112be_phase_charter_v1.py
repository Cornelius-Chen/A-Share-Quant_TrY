from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BEPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BEPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bc_phase_closure_payload: dict[str, Any],
        v112bd_phase_closure_payload: dict[str, Any],
        v112bb_phase_closure_payload: dict[str, Any],
    ) -> V112BEPhaseCharterReport:
        if not bool(dict(v112bc_phase_closure_payload.get("summary", {})).get("v112bc_success_criteria_met")):
            raise ValueError("V1.12BE requires the completed V1.12BC closure check.")
        if not bool(dict(v112bd_phase_closure_payload.get("summary", {})).get("v112bd_success_criteria_met")):
            raise ValueError("V1.12BE requires the completed V1.12BD closure check.")
        if not bool(dict(v112bb_phase_closure_payload.get("summary", {})).get("v112bb_success_criteria_met")):
            raise ValueError("V1.12BE requires the completed V1.12BB closure check.")

        charter = {
            "phase_name": "V1.12BE CPO Oracle Upper-Bound Benchmark",
            "mission": (
                "Run a hindsight-only upper-bound portfolio benchmark on the default 10-row guarded CPO layer "
                "to estimate the ex-post profit ceiling before no-leak portfolio tracks begin."
            ),
            "in_scope": [
                "oracle track only",
                "single-position or cash hindsight allocation",
                "equity curve and drawdown curve generation",
                "trade process trace",
            ],
            "out_of_scope": [
                "no-leak model training",
                "signal generation",
                "deployment",
            ],
            "success_criteria": [
                "the oracle benchmark is explicitly hindsight-only",
                "the benchmark uses the frozen default 10-row layer rather than a widened ad-hoc universe",
                "the benchmark outputs a reusable upper-bound portfolio trace for later comparison",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112be_cpo_oracle_upper_bound_benchmark",
            "do_open_v112be_now": True,
            "recommended_first_action": "freeze_v112be_cpo_oracle_upper_bound_benchmark_v1",
        }
        interpretation = [
            "V1.12BE exists to measure the hindsight profit ceiling without contaminating later no-leak experiments.",
            "The oracle benchmark is a benchmark line, not a trainable model line.",
        ]
        return V112BEPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112be_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BEPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
