from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134au_commercial_aerospace_post_exit_rebound_pattern_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_au_next_orthogonal_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        dominant_pattern = audit["summary"]["dominant_pattern"]
        delayed_rebound_share = float(audit["summary"]["delayed_rebound_share"])
        remaining_count = int(audit["summary"]["remaining_rebound_case_count"])

        promote_reentry_family = remaining_count > 0 and delayed_rebound_share >= 0.5

        triage_rows = [
            {
                "component": "sell_side_false_first_reversal_family",
                "status": "frozen_stopline",
                "detail": "This family has already collapsed into a singular residue.",
            },
            {
                "component": "next_orthogonal_family",
                "status": "post_exit_reentry_gap" if promote_reentry_family else "undecided",
                "detail": (
                    f"dominant_pattern = {dominant_pattern}, delayed_rebound_share = {delayed_rebound_share}, remaining_rebound_case_count = {remaining_count}"
                ),
            },
            {
                "component": "phase2_direction",
                "status": "stay_in_supervision_and_shift_from_sell_timing_to_reentry_supervision"
                if promote_reentry_family
                else "pause_new_family_search",
                "detail": "The remaining misses are more consistent with missing rebuild timing than with same-day sell timing.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134av_commercial_aerospace_au_next_orthogonal_direction_triage_v1",
            "authoritative_status": (
                "shift_next_supervision_to_post_exit_reentry_gap_family"
                if promote_reentry_family
                else "pause_after_local_deferral_stopline"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AV converts the post-exit rebound pattern audit into the next orthogonal direction judgment.",
            "If most remaining rebound-cost cases are negative on day 1 but positive later, the next family should be a rebuild or re-entry supervision family rather than another sell-side timing family.",
        ]
        return V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AVCommercialAerospaceAUNextOrthogonalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134av_commercial_aerospace_au_next_orthogonal_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
