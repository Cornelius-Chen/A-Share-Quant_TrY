from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Report:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.family_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_family_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_persistent_permission_confirmation_audit_v1.csv"
        )

    def analyze(self) -> V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Report:
        with self.family_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        for row in rows:
            row["open_to_60m"] = float(row["open_to_60m"])
            row["continuation_15_to_60m"] = float(row["continuation_15_to_60m"])
            row["burst_amount_share_15"] = float(row["burst_amount_share_15"])

        threshold_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for open_60_threshold in (0.01, 0.015):
            for continuation_threshold in (0.005, 0.01):
                for burst_cap in (0.32, 0.35, 0.40):
                    matched = [
                        row
                        for row in rows
                        if row["open_to_60m"] >= open_60_threshold
                        and row["continuation_15_to_60m"] >= continuation_threshold
                        and row["burst_amount_share_15"] <= burst_cap
                    ]
                    persistent_hits = sum(
                        1 for row in matched if row["permission_family"] == "persistent_permission_candidate"
                    )
                    counterfactual_hits = len(matched) - persistent_hits
                    precision = round(persistent_hits / len(matched), 8) if matched else 0.0
                    coverage = round(persistent_hits / 10.0, 8)
                    threshold_row = {
                        "open_to_60m_threshold": open_60_threshold,
                        "continuation_threshold": continuation_threshold,
                        "burst_amount_share_cap": burst_cap,
                        "matched_count": len(matched),
                        "persistent_hit_count": persistent_hits,
                        "counterfactual_hit_count": counterfactual_hits,
                        "precision": precision,
                        "coverage": coverage,
                    }
                    threshold_rows.append(threshold_row)
                    if best_row is None or (
                        threshold_row["precision"],
                        threshold_row["coverage"],
                        threshold_row["matched_count"],
                    ) > (
                        best_row["precision"],
                        best_row["coverage"],
                        best_row["matched_count"],
                    ):
                        best_row = threshold_row

        assert best_row is not None

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(threshold_rows[0].keys()))
            writer.writeheader()
            writer.writerows(threshold_rows)

        summary = {
            "acceptance_posture": "freeze_v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1",
            "threshold_row_count": len(threshold_rows),
            "best_open_to_60m_threshold": best_row["open_to_60m_threshold"],
            "best_continuation_threshold": best_row["continuation_threshold"],
            "best_burst_amount_share_cap": best_row["burst_amount_share_cap"],
            "best_matched_count": best_row["matched_count"],
            "best_persistent_hit_count": best_row["persistent_hit_count"],
            "best_counterfactual_hit_count": best_row["counterfactual_hit_count"],
            "best_precision": best_row["precision"],
            "best_coverage": best_row["coverage"],
            "threshold_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "inside the narrow add-permission family surface, first-hour continuation is the cleanest confirmation layer for persistent permission candidates"
            ),
        }
        interpretation = [
            "V1.34FF tests whether the new quantity-price permission families contain a narrower confirmation layer for persistent add permission.",
            "The goal is not to promote execution, only to see whether persistent candidates can be separated from fragile and failed counterfactuals with a simple continuation gate.",
        ]
        return V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Report(
            summary=summary,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
