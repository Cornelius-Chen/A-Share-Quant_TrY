from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AMPhaseCharterReport:
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


class V112AMPhaseCharterAnalyzer:
    def analyze(self, *, readiness_review_payload: dict[str, Any]) -> V112AMPhaseCharterReport:
        readiness_summary = dict(readiness_review_payload.get("summary", {}))
        if not bool(readiness_summary.get("bounded_training_pilot_lawful_now")):
            raise ValueError("V1.12AM requires V1.12AL to conclude that a bounded pilot is lawful.")

        if str(readiness_summary.get("bounded_training_pilot_scope")) != "extremely_small_core_skeleton_only":
            raise ValueError("V1.12AM only supports the extremely small core-skeleton pilot scope.")

        charter = {
            "phase_name": "V1.12AM CPO Extremely Small Core-Skeleton Training Pilot",
            "mission": (
                "Run a first extremely small CPO training pilot on the current core skeleton only, using the current "
                "truth-candidate rows, core labels, and stable implemented features under report-only boundaries."
            ),
            "in_scope": [
                "build a minimal sample set from current truth-candidate rows",
                "train an interpretable baseline and a bounded GBDT sidecar",
                "evaluate learnability of phase, role, and catalyst-sequence skeleton labels",
                "attach a small payoff-quality side reading without opening deployment rights",
            ],
            "out_of_scope": [
                "formal training promotion",
                "full feature-family implementation",
                "quiet-window or spillover truth promotion",
                "signal deployment",
            ],
            "success_criteria": [
                "the pilot exposes whether the current core skeleton is learnable at all",
                "the pilot produces model-comparison evidence without pretending representativeness",
                "the pilot remains report-only",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112am_cpo_extremely_small_core_skeleton_training_pilot",
            "do_open_v112am_now": True,
            "recommended_first_action": "freeze_v112am_cpo_extremely_small_core_skeleton_training_pilot_v1",
        }
        interpretation = [
            "V1.12AM exists to replace further abstract auditing with bounded failure exposure.",
            "The pilot is intentionally narrow: if it works, that does not open broad training rights; if it fails, that failure is still high-value information.",
        ]
        return V112AMPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112am_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AMPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
