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
class V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.slice_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_capital_mapping_diffusion_slice_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_capital_mapping_diffusion_summary_v1.csv"
        )

    def analyze(self) -> V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Report:
        rows = _read_csv(self.slice_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Window 006 capital-mapping diffusion outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "negative_sample_ready_count": sum(
                1 for row in summary_rows if row["final_training_admission"] == "negative_sample_ready"
            ),
            "not_tradable_count": sum(1 for row in rows if row["tradability_label"] == "not_tradable"),
            "negative_net_flow_count": sum(1 for row in rows if float(row["window_net_mf_amount"]) < 0.0),
        }
        interpretation = [
            "Window 006 now has a concrete symbol-level diffusion slice rather than a vague concept-caution label.",
            "The narrative spread was real, but lawful board alignment was absent and the main mapping names never built a clean repricing leg.",
            "This is the correct anti-pattern for concept spread without structure.",
        ]
        return V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ba_commercial_aerospace_window_capital_mapping_diffusion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
