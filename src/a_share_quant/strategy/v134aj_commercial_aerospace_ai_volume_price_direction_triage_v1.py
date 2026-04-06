from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ai_commercial_aerospace_reversal_volume_price_confirmation_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ai_volume_price_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        strongest = audit["summary"]["strongest_feature"]
        strongest_gap = audit["summary"]["strongest_feature_gap_rebound_minus_followthrough"]

        triage_rows = [
            {
                "component": "volume_price_confirmation_layer",
                "status": "retain_as_supervision_only",
                "detail": f"strongest_feature = {strongest}, gap = {strongest_gap}",
            },
            {
                "component": "execution_rule_change",
                "status": "not_yet_authorized",
                "detail": "The audit measures separation only; it does not authorize direct rule edits yet.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Volume-price confirmation remains a supervisory refinement inside phase 2.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134aj_commercial_aerospace_ai_volume_price_direction_triage_v1",
            "authoritative_status": "retain_volume_price_confirmation_as_supervision_only_inside_current_phase2_reference",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AJ turns the first reversal-focused volume-price confirmation audit into the next supervision judgment.",
            "The branch keeps the layer as supervision only until the separation is stable enough to justify a narrower local rule experiment.",
        ]
        return V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AJCommercialAerospaceAIVolumePriceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134aj_commercial_aerospace_ai_volume_price_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
