from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cj_commercial_aerospace_local_rebound_residue_registry_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cj_local_rebound_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Report:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        summary = registry["summary"]

        triage_rows = [
            {
                "component": "local_rebound_residue_registry",
                "status": "retain_supervision_only",
                "detail": (
                    f"residue_seed_count = {summary['residue_seed_count']}, "
                    f"top_residue_case = {summary['top_residue_case']}"
                ),
            },
            {
                "component": "persistent_vs_transient_split",
                "status": "mandatory",
                "detail": (
                    f"persistent_rebound_residue_count = {summary['persistent_rebound_residue_count']}, "
                    f"transient_rebound_residue_count = {summary['transient_rebound_residue_count']}"
                ),
            },
            {
                "component": "next_real_work",
                "status": "stay_local_case_supervision_only",
                "detail": "If the branch keeps going, it should only inspect these residue cases locally; do not reopen broader sell-family tuning or replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1",
            "authoritative_status": "retain_local_rebound_residue_registry_as_supervision_only_and_stop_broad_reduce_tuning",
            "residue_seed_count": summary["residue_seed_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CK converts the remaining medium-short rebound residue into a narrow direction judgment.",
            "The branch should now stop broad reduce tuning and only keep these residue cases as supervision if it needs any further local inspection.",
        ]
        return V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
