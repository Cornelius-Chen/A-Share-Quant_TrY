from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.stack_path = analysis_dir / "v134ae_commercial_aerospace_phase2_current_shadow_stack_v3.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ae_phase2_current_direction_triage_v3.csv"
        )

    def analyze(self) -> V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Report:
        stack = json.loads(self.stack_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "current_phase2_wider_reference",
                "status": "frozen",
                "detail": stack["summary"]["current_phase2_wider_reference"],
            },
            {
                "component": "multi_stage_sell_ladder_refinement",
                "status": "promoted_inside_current_wider_reference",
                "detail": (
                    f"best_reversal_fraction = {stack['summary']['best_reversal_fraction']} under the same-day shadow objective"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "The sell-ladder refinement does not authorize expansion beyond the current broader-hit boundary.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The sell-ladder refinement remains shadow-only and does not bind into replay.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134af_commercial_aerospace_ae_phase2_current_direction_triage_v3",
            "authoritative_status": "freeze_phase2_shadow_stack_v3_and_keep_all_session_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AF converts the multi-stage sell-fraction supervision pass into the current phase-2 direction judgment.",
            "The branch should treat the new wider reference as current while explicitly remembering that the optimization target is still same-day shadow benefit, not replay readiness.",
        ]
        return V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AFCommercialAerospaceAEPhase2CurrentDirectionTriageV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134af_commercial_aerospace_ae_phase2_current_direction_triage_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
