from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BFCommercialAerospaceBELockoutDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BFCommercialAerospaceBELockoutDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_be_lockout_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BFCommercialAerospaceBELockoutDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        seed_count = int(audit["summary"]["lockout_seed_count"])
        earliest = audit["summary"]["earliest_lockout_seed_trade_date"]
        cooldown = audit["summary"]["suggested_min_cooldown_trading_days"]

        triage_rows = [
            {
                "component": "board_cooling_lockout_seed",
                "status": "retained_as_supervision",
                "detail": f"lockout_seed_count = {seed_count}, earliest_lockout_seed_trade_date = {earliest}",
            },
            {
                "component": "reentry_ladder_override",
                "status": "approved_as_upper_governance_veto",
                "detail": (
                    "When board-level lockout is active, seed-level reentry ladder should remain subordinate. "
                    f"suggested_min_cooldown_trading_days = {cooldown}."
                ),
            },
            {
                "component": "execution_binding",
                "status": "still_blocked",
                "detail": "Lockout remains supervision-only and does not reopen replay or authorize live binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bf_commercial_aerospace_be_lockout_direction_triage_v1",
            "authoritative_status": "freeze_board_cooling_lockout_supervision_and_continue_board_level_governance_only",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BF converts the new board-level cooling audit into the next direction judgment.",
            "The lockout seed may sit above seed-level reentry supervision, but it remains governance-only and does not authorize execution binding.",
        ]
        return V134BFCommercialAerospaceBELockoutDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BFCommercialAerospaceBELockoutDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BFCommercialAerospaceBELockoutDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bf_commercial_aerospace_be_lockout_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
