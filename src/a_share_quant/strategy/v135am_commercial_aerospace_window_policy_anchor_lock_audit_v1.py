from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{str(k).lstrip("\ufeff"): v for k, v in row.items()} for row in csv.DictReader(handle)]


@dataclass(slots=True)
class V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.lock_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_policy_anchor_lock_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_policy_anchor_lock_summary_v1.csv"
        )

    def analyze(self) -> V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Report:
        rows = _read_csv(self.lock_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Window policy anchor lock outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "direction_anchor_count": sum(1 for row in rows if row["anchor_strength"] == "p0"),
            "reinforcement_anchor_count": sum(1 for row in rows if row["anchor_strength"] == "p1"),
            "exact_january_ignition_text_locked_count": sum(
                1 for row in rows if row["is_exact_january_ignition_text"] == "true"
            ),
            "gate_hold_count": sum(
                1 for row in summary_rows if row["final_training_admission"] == "hold_until_policy_wording_locked"
            ),
        }
        interpretation = [
            "Window 002 now has a locked policy stack rather than a vague policy story.",
            "The strict conclusion is not that January lacked policy support, but that the exact January 8/12 ignition text is still not locked.",
            "This artifact prevents premature final-training admission while preserving the genuine top-down backdrop.",
        ]
        return V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135am_commercial_aerospace_window_policy_anchor_lock_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
