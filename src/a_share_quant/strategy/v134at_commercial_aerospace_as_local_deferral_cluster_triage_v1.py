from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134as_commercial_aerospace_local_deferral_cluster_singularity_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_as_local_deferral_cluster_triage_v1.csv"
        )

    def analyze(self) -> V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        match_share = float(audit["summary"]["matched_local_deferral_share_of_reversal"])
        matched_count = int(audit["summary"]["matched_local_deferral_count"])
        stopline = matched_count <= 1 or match_share <= 0.10

        triage_rows = [
            {
                "component": "local_deferral_cluster_size",
                "status": "singular_residue" if stopline else "still_plural_cluster",
                "detail": (
                    f"matched_count = {matched_count}, match_share = {match_share}"
                ),
            },
            {
                "component": "same_family_local_refinement_search",
                "status": "stopline_reached" if stopline else "keep_searching",
                "detail": "Do not keep mining the same false-first-reversal family once only a singular residue remains.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The singularity result does not change replay readiness.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134at_commercial_aerospace_as_local_deferral_cluster_triage_v1",
            "authoritative_status": (
                "freeze_current_local_deferral_and_stop_same_family_search"
                if stopline
                else "keep_searching_same_family_local_deferrals"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AT decides whether the promoted local deferral is the last worthwhile point-in-time refinement in this family.",
            "A singular residue means the branch should freeze the current refinement and stop spending more budget on the same family.",
        ]
        return V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ATCommercialAerospaceASLocalDeferralClusterTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134at_commercial_aerospace_as_local_deferral_cluster_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
