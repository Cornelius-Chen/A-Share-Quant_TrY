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
class V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.slice_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_subtheme_misalignment_slice_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_subtheme_misalignment_summary_v1.csv"
        )

    def analyze(self) -> V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Report:
        rows = _read_csv(self.slice_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Window 005 subtheme misalignment outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "not_tradable_count": sum(1 for row in rows if row["tradability_label"] == "not_tradable"),
            "watch_only_count": sum(
                1 for row in rows if row["tradability_label"] in {"watch_confirmation_only", "watch_pullback_only"}
            ),
            "negative_sample_ready_count": sum(
                1 for row in summary_rows if row["final_training_admission"] == "negative_sample_ready"
            ),
        }
        interpretation = [
            "Window 005 is now pinned as a clean logic-valid-but-board-misaligned sample.",
            "The most important evidence is that the target subtheme core failed to confirm while a few local outliers still looked strong.",
            "This should train the model not to upgrade a good industrial logic into a tradable new leg without breadth and core-name confirmation.",
        ]
        return V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135aq_commercial_aerospace_window_subtheme_misalignment_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
