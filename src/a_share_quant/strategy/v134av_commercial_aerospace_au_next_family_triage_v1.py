from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AVCommercialAerospaceAUNextFamilyTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AVCommercialAerospaceAUNextFamilyTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134au_commercial_aerospace_next_orthogonal_family_scan_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_au_next_family_triage_v1.csv"
        )

    def analyze(self) -> V134AVCommercialAerospaceAUNextFamilyTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        residue_hits = int(audit["summary"]["best_remaining_rebound_cost_hit_count"])
        other_hits = int(audit["summary"]["best_other_hit_count"])
        approved = residue_hits >= 2

        triage_rows = [
            {
                "component": "next_orthogonal_family",
                "status": "approved_for_targeted_supervision" if approved else "not_yet_worth_pursuing",
                "detail": (
                    "oscillatory_breakdown_churn"
                    f" | residue_hits = {residue_hits}, other_hits = {other_hits}"
                ),
            },
            {
                "component": "orthogonality_claim",
                "status": "pass" if approved else "weak",
                "detail": "This family is about repeated reversal/severe churn, not a false first reversal that cleanly reclaims and then fails again.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The new family, if pursued, still begins as supervision-only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134av_commercial_aerospace_au_next_family_triage_v1",
            "authoritative_status": (
                "pursue_oscillatory_breakdown_churn_as_next_targeted_supervision_family"
                if approved
                else "do_not_open_next_family_yet"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AV converts the orthogonal family scan into a next-step judgment.",
            "Approval here still means targeted supervision only, not replay or surface expansion.",
        ]
        return V134AVCommercialAerospaceAUNextFamilyTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AVCommercialAerospaceAUNextFamilyTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AVCommercialAerospaceAUNextFamilyTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134av_commercial_aerospace_au_next_family_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
