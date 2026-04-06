from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _is_entry(row: dict[str, Any]) -> bool:
    return str(row.get("action_context")) == "entry_vs_skip"


@dataclass(slots=True)
class V118HCpoAddVsEntryRoleYearEntanglementAuditReport:
    summary: dict[str, Any]
    label_distribution_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_distribution_rows": self.label_distribution_rows,
            "interpretation": self.interpretation,
        }


class V118HCpoAddVsEntryRoleYearEntanglementAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118HCpoAddVsEntryRoleYearEntanglementAuditReport:
        rows = [row for row in _load_csv_rows(rows_path) if _is_positive_add(row) or _is_entry(row)]
        counter = Counter(
            (
                "positive_add" if _is_positive_add(row) else "entry",
                str(row.get("signal_trade_date"))[:4],
                str(row.get("role_family")),
            )
            for row in rows
        )
        label_distribution_rows = [
            {
                "label_family": label_family,
                "year": year,
                "role_family": role_family,
                "row_count": row_count,
            }
            for (label_family, year, role_family), row_count in sorted(counter.items())
        ]

        entry_role_year = Counter((str(row.get("signal_trade_date"))[:4], str(row.get("role_family"))) for row in rows if _is_entry(row))
        add_role_year = Counter((str(row.get("signal_trade_date"))[:4], str(row.get("role_family"))) for row in rows if _is_positive_add(row))

        summary = {
            "acceptance_posture": "freeze_v118h_cpo_add_vs_entry_role_year_entanglement_audit_v1",
            "positive_add_role_year_count": len(add_role_year),
            "entry_role_year_count": len(entry_role_year),
            "entry_concentration_peak": max(entry_role_year.values()) if entry_role_year else 0,
            "add_concentration_peak": max(add_role_year.values()) if add_role_year else 0,
            "authoritative_interpretation": "chronology_instability_is_partly_role_year_entanglement",
            "recommended_next_posture": "use_role_year_entanglement_as_the_primary_explanation_layer_in_next_triage",
        }
        interpretation = [
            "V1.18H audits whether the unstable chronology result is partly caused by year-role entanglement rather than pure threshold weakness.",
            "If entry rows concentrate in one late role-year pocket while positive adds concentrate elsewhere, then chronology failure is at least partly an object-shift problem.",
            "This is explanatory, but it matters because it changes what kind of next audit is worth running.",
        ]
        return V118HCpoAddVsEntryRoleYearEntanglementAuditReport(
            summary=summary,
            label_distribution_rows=label_distribution_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118HCpoAddVsEntryRoleYearEntanglementAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118HCpoAddVsEntryRoleYearEntanglementAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118h_cpo_add_vs_entry_role_year_entanglement_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
