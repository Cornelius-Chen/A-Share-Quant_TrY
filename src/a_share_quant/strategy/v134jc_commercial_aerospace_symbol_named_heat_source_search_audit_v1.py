from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Report:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_symbol_named_heat_source_search_v1.csv"
        )

    def _load_events(self) -> list[dict[str, Any]]:
        path = (
            self.repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Report:
        rows = self._load_events()
        source_rows: list[dict[str, Any]] = []

        for row in rows:
            registry_id = row["registry_id"]
            if registry_id not in {"ca_source_004", "ca_source_007", "ca_source_012", "ca_anchor_004"}:
                continue

            if registry_id == "ca_source_007":
                source_class = "retained_symbol_named_turning_point_heat_source"
                search_reading = (
                    "hard symbol-named theme-heat source retained as decisive turning-point evidence"
                )
            elif registry_id in {"ca_source_004", "ca_source_012"}:
                source_class = "discarded_symbol_list_theme_heat_source"
                search_reading = (
                    "theme-heat source contains strong names but is explicitly discarded as non-decisive and therefore cannot thicken the hard counterpanel"
                )
            else:
                source_class = "forward_unresolved_manual_heat_anchor"
                search_reading = (
                    "manual forward anchor records a future sentiment-transition class but is unresolved and cannot count as a historical symbol-named hard source"
                )

            source_rows.append(
                {
                    "registry_id": registry_id,
                    "record_type": row["record_type"],
                    "layer": row["layer"],
                    "source_name": row["source_name"],
                    "event_scope": row["event_scope"],
                    "decisive_semantic": row["decisive_semantic"],
                    "decisive_reason": row["decisive_reason"],
                    "decisive_retained": row["decisive_retained"],
                    "source_class": source_class,
                    "search_reading": search_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
            writer.writeheader()
            writer.writerows(source_rows)

        retained_symbol_named_count = sum(
            1 for row in source_rows if row["source_class"] == "retained_symbol_named_turning_point_heat_source"
        )
        summary = {
            "acceptance_posture": "freeze_v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1",
            "searched_source_count": len(source_rows),
            "retained_symbol_named_heat_source_count": retained_symbol_named_count,
            "second_symbol_named_heat_source_found": retained_symbol_named_count >= 2,
            "discarded_theme_heat_source_count": sum(
                1 for row in source_rows if row["source_class"] == "discarded_symbol_list_theme_heat_source"
            ),
            "forward_unresolved_heat_anchor_count": sum(
                1 for row in source_rows if row["source_class"] == "forward_unresolved_manual_heat_anchor"
            ),
            "search_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the current local commercial-aerospace event source universe still contains only one retained symbol-named hard heat source: ca_source_007; discarded theme-heat lists and unresolved manual anchors do not create a second hard counterpanel",
        }
        interpretation = [
            "V1.34JC shifts the search from strong symbols to hard event-source inventory.",
            "The current negative result is meaningful: the hard counterpanel remains single-case because the local event universe itself only contains one retained symbol-named decisive heat source.",
        ]
        return V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Report(
            summary=summary,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
