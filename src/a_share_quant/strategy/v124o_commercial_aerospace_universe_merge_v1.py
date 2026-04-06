from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124OCommercialAerospaceUniverseMergeReport:
    summary: dict[str, Any]
    merged_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "merged_rows": self.merged_rows,
            "interpretation": self.interpretation,
        }


class V124OCommercialAerospaceUniverseMergeAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_path = repo_root / "data" / "training" / "commercial_aerospace_web_concept_universe_v1.csv"
        self.wave2_path = repo_root / "data" / "training" / "commercial_aerospace_universe_wave2_v1.csv"

    def _load_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V124OCommercialAerospaceUniverseMergeReport:
        base_rows = self._load_csv(self.base_path)
        wave2_rows = self._load_csv(self.wave2_path)

        merged: dict[str, dict[str, Any]] = {}
        for row in base_rows:
            merged[row["symbol"]] = {
                "symbol": row["symbol"],
                "name": row["name"],
                "group": row["group"],
                "subgroup": row["subgroup"],
                "confidence": "base_retained",
                "source_layer": "wave1",
                "reason": row["rationale"],
            }
        for row in wave2_rows:
            merged.setdefault(
                row["symbol"],
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "group": row["group"],
                    "subgroup": row["subgroup"],
                    "confidence": row["confidence"],
                    "source_layer": "wave2",
                    "reason": row["reason"],
                },
            )

        merged_rows = sorted(merged.values(), key=lambda row: (row["group"], row["symbol"]))
        summary = {
            "acceptance_posture": "freeze_v124o_commercial_aerospace_universe_merge_v1",
            "base_count": len(base_rows),
            "wave2_added_count": len(wave2_rows),
            "merged_count": len(merged_rows),
            "group_counts": {
                group: sum(1 for row in merged_rows if row["group"] == group)
                for group in sorted({row["group"] for row in merged_rows})
            },
            "recommended_next_posture": "use_merged_universe_as_input_to_universe_triage_or_control_extraction_depending_adversarial_review",
        }
        interpretation = [
            "V1.24O merges the retained wave1 universe and the confidence-tagged wave2 additions into one working table.",
            "This is not a claim that every merged name is equally authoritative.",
            "It is simply the cleanest handoff artifact for the next step.",
        ]
        return V124OCommercialAerospaceUniverseMergeReport(
            summary=summary,
            merged_rows=merged_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124OCommercialAerospaceUniverseMergeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_csv(*, data_dir: Path, result: V124OCommercialAerospaceUniverseMergeReport) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "commercial_aerospace_merged_universe_v1.csv"
    fieldnames = ["symbol", "name", "group", "subgroup", "confidence", "source_layer", "reason"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.merged_rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124OCommercialAerospaceUniverseMergeAnalyzer(repo_root)
    result = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124o_commercial_aerospace_universe_merge_v1",
        result=result,
    )
    csv_path = write_csv(
        data_dir=repo_root / "data" / "training",
        result=result,
    )
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
