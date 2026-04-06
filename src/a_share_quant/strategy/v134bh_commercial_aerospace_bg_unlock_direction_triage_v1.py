from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BHCommercialAerospaceBGUnlockDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BHCommercialAerospaceBGUnlockDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bg_unlock_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BHCommercialAerospaceBGUnlockDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "board_revival_unlock_seed",
                "status": "retained_as_supervision",
                "detail": (
                    f"positive_seed_count = {audit['summary']['positive_seed_count']}, "
                    f"false_bounce_seed_count = {audit['summary']['false_bounce_seed_count']}."
                ),
            },
            {
                "component": "lockout_release_condition",
                "status": "approved_as_board_level_guard",
                "detail": "Lockout release discussion must require broad revival seed, not small-range rebound.",
            },
            {
                "component": "execution_binding",
                "status": "still_blocked",
                "detail": "Unlock supervision remains governance-only and does not authorize reentry simulation or replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bh_commercial_aerospace_bg_unlock_direction_triage_v1",
            "authoritative_status": "freeze_board_revival_unlock_supervision_and_continue_board_level_unlock_governance_only",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BH turns the board revival unlock audit into the next direction judgment.",
            "The unlock seed may release the cooling lockout only in governance, but it still does not authorize execution binding or simulator work.",
        ]
        return V134BHCommercialAerospaceBGUnlockDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BHCommercialAerospaceBGUnlockDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BHCommercialAerospaceBGUnlockDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bh_commercial_aerospace_bg_unlock_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
