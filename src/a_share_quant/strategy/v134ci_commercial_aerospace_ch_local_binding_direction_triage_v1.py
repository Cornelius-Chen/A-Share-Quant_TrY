from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ch_local_binding_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]

        triage_rows = [
            {
                "component": "same_day_core_contribution",
                "status": "retain",
                "detail": f"best_same_day_symbol = {summary['best_same_day_symbol']}",
            },
            {
                "component": "medium_short_rebound_residue",
                "status": "local_enough_for_case_supervision_only",
                "detail": (
                    f"worst_3d_rebound_symbol = {summary['worst_3d_rebound_symbol']}, "
                    f"top_3d_rebound_case = {summary['top_3d_rebound_case']}"
                ),
            },
            {
                "component": "next_real_work",
                "status": "stay_local_and_do_not_expand",
                "detail": "Any next work should stay inside the local rebound residue and should not reopen wider surface expansion or replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134ci_commercial_aerospace_ch_local_binding_direction_triage_v1",
            "authoritative_status": "retain_isolated_sell_side_binding_surface_and_shift_next_to_local_rebound_residue_supervision_only",
            "positive_3d_rebound_case_count": summary["positive_3d_rebound_case_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CI converts local attribution on the first real binding surface into a narrowed direction judgment.",
            "The remaining issue is no longer a broad sell-family failure; it is a local rebound residue that should remain under supervision only.",
        ]
        return V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ci_commercial_aerospace_ch_local_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
