from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134au_commercial_aerospace_orthogonal_failure_family_scan_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_au_orthogonal_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        strongest_gap = abs(float(audit["summary"]["strongest_primary_gap"]))
        strongest_name = audit["summary"]["strongest_family_name"]
        openable = strongest_gap >= 5.0

        triage_rows = [
            {
                "component": "next_orthogonal_family_candidate",
                "status": "weak_candidate_only" if not openable else "open_first_audit",
                "detail": f"{strongest_name}, primary_gap = {strongest_gap}",
            },
            {
                "component": "same_family_false_first_reversal",
                "status": "already_at_stopline",
                "detail": "Do not reopen the false-first-reversal family after singularity was confirmed.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Orthogonal-family scanning does not change replay readiness.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134av_commercial_aerospace_au_orthogonal_direction_triage_v1",
            "authoritative_status": (
                f"retain_{strongest_name}_as_weak_candidate_only"
                if not openable
                else f"open_{strongest_name}_first_audit"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AV converts the orthogonal-family quick scan into the next supervision direction judgment.",
            "A weak candidate means the branch should name the next likely family but avoid opening another deep local line yet.",
        ]
        return V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AVCommercialAerospaceAUOrthogonalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134av_commercial_aerospace_au_orthogonal_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
