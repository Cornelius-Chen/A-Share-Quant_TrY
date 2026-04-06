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
class V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.ledger_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_admission_ledger_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_admission_ledger_summary_v1.csv"
        )

    def analyze(self) -> V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Report:
        rows = _read_csv(self.ledger_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Commercial aerospace training admission ledger outputs are missing.")
        summary = {
            "row_count": len(rows),
            "positive_support_sample_ready_count": sum(
                1 for row in rows if row["training_admission_class"] == "positive_support_sample_ready"
            ),
            "negative_support_sample_ready_count": sum(
                1 for row in rows if row["training_admission_class"] == "negative_support_sample_ready"
            ),
            "positive_sample_ready_count": sum(
                1 for row in rows if row["training_admission_class"] == "positive_sample_ready"
            ),
            "negative_sample_ready_count": sum(
                1 for row in rows if row["training_admission_class"] == "negative_sample_ready"
            ),
            "bridge_sample_ready_count": sum(
                1 for row in rows if row["training_admission_class"] == "bridge_sample_ready"
            ),
            "subwindow_learning_only_count": sum(
                1 for row in rows if row["training_admission_class"] == "subwindow_learning_only"
            ),
            "hold_count": sum(1 for row in rows if row["supervisor_release_state"] == "hold"),
            "under_review_count": sum(1 for row in rows if row["supervisor_release_state"] == "not_released"),
        }
        interpretation = [
            "The ledger now separates released samples from windows still under hold or under review.",
            "Window 001 is now correctly released as a positive support sample rather than being left in an overly conservative under-review bucket.",
            "Window 004 is now correctly separated into a negative-support bucket instead of being left stuck in under-review.",
            "The strict core conclusion is that window 002 remains the only high-value primary-positive archetype still blocked by the policy gate.",
            "This ledger is the correct boundary between engineering completion and future model-training admission.",
        ]
        return V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135au_commercial_aerospace_training_admission_ledger_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
