from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ADCommercialAerospaceACReversalFractionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ADCommercialAerospaceACReversalFractionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ac_reversal_fraction_triage_v1.csv"
        )

    def analyze(self) -> V134ADCommercialAerospaceACReversalFractionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        best_fraction = audit["summary"]["best_reversal_fraction"]
        current_fraction = audit["summary"]["current_reversal_fraction"]
        delta = audit["summary"]["same_day_loss_avoided_delta"]

        promote = best_fraction != current_fraction and delta > 0
        triage_rows = [
            {
                "component": "reversal_sell_fraction",
                "status": "promote_inside_current_wider_reference" if promote else "keep_current_fraction",
                "detail": (
                    f"best_reversal_fraction = {best_fraction}, delta = {delta}"
                    if promote
                    else f"current_fraction = {current_fraction} remains acceptable"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "This supervision step only changes the internal sell ladder inside the existing broader-hit boundary.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Reversal sell-fraction tuning remains a phase-2 shadow refinement only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ad_commercial_aerospace_ac_reversal_fraction_triage_v1",
            "authoritative_status": (
                "promote_best_reversal_fraction_inside_current_wider_reference"
                if promote
                else "keep_current_reversal_fraction_inside_current_wider_reference"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AD converts the reversal sell-fraction audit into the next local supervision judgment.",
            "The branch is only allowed to promote a different fraction if the same-day-loss-avoided improvement is positive without changing the existing broader-hit surface boundary.",
        ]
        return V134ADCommercialAerospaceACReversalFractionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ADCommercialAerospaceACReversalFractionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ADCommercialAerospaceACReversalFractionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ad_commercial_aerospace_ac_reversal_fraction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
