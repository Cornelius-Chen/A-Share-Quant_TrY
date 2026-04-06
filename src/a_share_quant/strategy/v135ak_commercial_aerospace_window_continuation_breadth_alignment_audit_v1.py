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
class V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.alignment_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_continuation_breadth_alignment_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_continuation_breadth_alignment_summary_v1.csv"
        )

    def analyze(self) -> V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Report:
        rows = _read_csv(self.alignment_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Continuation breadth alignment outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "broad_confirmation_real_count": sum(
                1 for row in rows if row["breadth_alignment_state"] == "broad_confirmation_real"
            ),
            "continuation_not_upgraded_count": sum(
                1 for row in rows if row["breadth_alignment_state"] == "continuation_not_upgraded"
            ),
            "breadth_failed_count": sum(
                1 for row in rows if row["breadth_alignment_state"] == "breadth_failed"
            ),
            "full_window_hold_count": sum(
                1
                for row in summary_rows
                if row["final_training_admission"] == "subwindow_ready_but_full_window_not_ready"
            ),
        }
        interpretation = [
            "Window 008 now has explicit board-breadth evidence across December, January, and February.",
            "The strict result is not that the conference chain was fake, but that a real December confirmation did not upgrade into a durable continuation.",
            "This artifact should prevent the model from confusing one strong catalyst month with a persistent multi-month primary leg.",
        ]
        return V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ak_commercial_aerospace_window_continuation_breadth_alignment_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
