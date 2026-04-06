from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.stack_path = analysis_dir / "v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.json"
        self.triage_path = analysis_dir / "v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_aq_phase2_current_direction_triage_v4.csv"
        )

    def analyze(self) -> V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Report:
        stack = json.loads(self.stack_path.read_text(encoding="utf-8"))
        local_triage = json.loads(self.triage_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "current_phase2_wider_reference",
                "status": "frozen",
                "detail": stack["summary"]["current_phase2_wider_reference"],
            },
            {
                "component": "local_reversal_deferral_refinement",
                "status": local_triage["summary"]["authoritative_status"],
                "detail": f"local_deferral_same_day_delta = {stack['summary']['local_deferral_same_day_delta']}",
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "The local deferral refinement does not authorize expansion beyond broader-hit sessions.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The local deferral refinement remains phase-2 shadow-only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ar_commercial_aerospace_aq_phase2_current_direction_triage_v4",
            "authoritative_status": "freeze_phase2_shadow_stack_v4_and_keep_all_session_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AR converts the local reversal-deferral experiment into the next phase-2 direction judgment.",
            "The branch keeps the same blocked boundaries while allowing a tiny local point-in-time refinement inside the current wider reference.",
        ]
        return V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ARCommercialAerospaceAQPhase2CurrentDirectionTriageV4Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ar_commercial_aerospace_aq_phase2_current_direction_triage_v4",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
