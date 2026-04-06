from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bk_local_only_rebound_triage_v1.csv"
        )

    def analyze(self) -> V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "local_only_rebound_seed",
                "status": "retained_as_board_false_bounce_guard",
                "detail": f"local_only_rebound_seed_count = {audit['summary']['local_only_rebound_seed_count']}.",
            },
            {
                "component": "unlock_override",
                "status": "blocked",
                "detail": "Local-only rebound seeds cannot release board_cooling_lockout or substitute for board_revival_unlock.",
            },
            {
                "component": "symbol_reentry_interpretation",
                "status": "subordinate_only",
                "detail": "When this guard fires, strong symbols may be watched but board-level reentry discussion stays blocked.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bl_commercial_aerospace_bk_local_only_rebound_triage_v1",
            "authoritative_status": "freeze_local_only_rebound_guard_and_keep_board_unlock_strict",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BL turns local-only rebound seeds into a direction judgment.",
            "The branch should treat these days as evidence that a few names are strong inside a weak board, not as evidence that the board lockout is over.",
        ]
        return V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BLCommercialAerospaceBKLocalOnlyReboundTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bl_commercial_aerospace_bk_local_only_rebound_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
