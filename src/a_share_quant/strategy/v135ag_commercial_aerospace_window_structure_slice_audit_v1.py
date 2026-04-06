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
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V135AGCommercialAerospaceWindowStructureSliceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AGCommercialAerospaceWindowStructureSliceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.structure_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_structure_slice_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_training_admission_summary_v1.csv"
        )

    def analyze(self) -> V135AGCommercialAerospaceWindowStructureSliceAuditV1Report:
        structure_rows = _read_csv(self.structure_path)
        summary_rows = _read_csv(self.summary_path)
        if not structure_rows:
            raise FileNotFoundError(self.structure_path)
        summary = {
            "structure_row_count": len(structure_rows),
            "covered_window_count": len({row["sample_window_id"] for row in structure_rows}),
            "tradable_now_count": sum(1 for row in structure_rows if row["tradability_label"] == "tradable_now"),
            "watch_only_count": sum(
                1
                for row in structure_rows
                if row["tradability_label"] in {"watch_pullback_only", "watch_confirmation_only"}
            ),
            "not_tradable_count": sum(1 for row in structure_rows if row["tradability_label"] == "not_tradable"),
            "negative_sample_ready_count": sum(
                1 for row in summary_rows if row["admission_state"] == "negative_sample_ready"
            ),
            "policy_hold_window_count": sum(
                1 for row in summary_rows if row["admission_state"] == "hold_until_policy_wording_locked"
            ),
            "subwindow_ready_count": sum(
                1 for row in summary_rows if row["admission_state"] == "subwindow_ready_but_full_window_not_ready"
            ),
        }
        interpretation = [
            "This slice turns three high-value commercial-aerospace training windows into price-structure evidence instead of pure event narration.",
            "The January ignition window now has representative structure rows but still stays behind a policy-wording gate.",
            "The conference-chain window now contains both a late-December selective-diffusion subwindow and a weak February followthrough slice, so it is still not a full-window training pass.",
            "The March launch cluster is strong enough as a negative sample because official milestones failed to reopen the board.",
        ]
        return V135AGCommercialAerospaceWindowStructureSliceAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AGCommercialAerospaceWindowStructureSliceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AGCommercialAerospaceWindowStructureSliceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ag_commercial_aerospace_window_structure_slice_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
