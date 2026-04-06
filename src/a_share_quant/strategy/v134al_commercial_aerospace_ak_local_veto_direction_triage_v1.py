from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ak_local_veto_direction_triage_v1.csv"
        )

    def analyze(self) -> V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        precision = audit["summary"]["best_precision_rebound"]
        coverage = audit["summary"]["best_rebound_coverage"]
        follow_hits = audit["summary"]["best_followthrough_hit_count"]

        promotable = precision >= 0.75 and follow_hits <= 1
        triage_rows = [
            {
                "component": "local_rebound_cost_veto",
                "status": "promote_local_experiment" if promotable else "retain_as_supervision_only",
                "detail": f"precision = {precision}, coverage = {coverage}, followthrough_hit_count = {follow_hits}",
            },
            {
                "component": "phase2_wider_reference",
                "status": "unchanged_for_now",
                "detail": "The local veto scan itself does not change the current wider reference unless the precision is convincingly narrow.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Any local veto remains supervision-only until separately audited inside the phase-2 simulator.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134al_commercial_aerospace_ak_local_veto_direction_triage_v1",
            "authoritative_status": (
                "promote_local_rebound_cost_veto_experiment"
                if promotable
                else "retain_local_rebound_cost_veto_as_supervision_only"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AL turns the local rebound-cost veto scan into the next supervision judgment.",
            "Only a very clean, very narrow veto is allowed to move on to the next experiment; otherwise the clue remains supervision-only.",
        ]
        return V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ALCommercialAerospaceAKLocalVetoDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134al_commercial_aerospace_ak_local_veto_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
