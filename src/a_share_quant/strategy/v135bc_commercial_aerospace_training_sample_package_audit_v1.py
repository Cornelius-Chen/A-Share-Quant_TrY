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
class V135BCCommercialAerospaceTrainingSamplePackageAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135BCCommercialAerospaceTrainingSamplePackageAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.package_path = (
            repo_root / "data" / "training" / "commercial_aerospace_202511_202604_training_sample_package_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_training_sample_package_summary_v1.csv"
        )

    def analyze(self) -> V135BCCommercialAerospaceTrainingSamplePackageAuditV1Report:
        rows = _read_csv(self.package_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Commercial aerospace training sample package outputs are missing.")
        summary = {
            "row_count": len(rows),
            "primary_fit_count": sum(1 for row in rows if row["package_tier"] == "primary_fit"),
            "auxiliary_fit_count": sum(1 for row in rows if row["package_tier"] == "auxiliary_fit"),
            "reference_only_count": sum(1 for row in rows if row["package_tier"] == "reference_only"),
            "locked_holdout_count": sum(1 for row in rows if row["package_tier"] == "locked_holdout"),
            "primary_positive_fit_count": sum(
                1
                for row in rows
                if row["package_tier"] == "primary_fit" and "positive" in row["training_admission_class"]
            ),
        }
        interpretation = [
            "The package is intentionally not a raw export of the ledger; it applies stricter fitting tiers.",
            "Window 002 remains locked, window 008 remains reference-only, and only clean released negative windows enter primary fit.",
            "Auxiliary fit is reserved for support, bridge, and non-final positive context windows.",
        ]
        return V135BCCommercialAerospaceTrainingSamplePackageAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BCCommercialAerospaceTrainingSamplePackageAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BCCommercialAerospaceTrainingSamplePackageAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135bc_commercial_aerospace_training_sample_package_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
