from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TARGET_NAMES = (
    "航天发展",
    "中国卫通",
    "再升科技",
    "西测测试",
    "华菱线缆",
    "鲁信创投",
    "金风科技",
    "电广传媒",
    "张江高科",
    "斯瑞新材",
    "臻镭科技",
)


@dataclass(slots=True)
class V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Report:
    summary: dict[str, Any]
    gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "gap_rows": self.gap_rows,
            "interpretation": self.interpretation,
        }


class V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.utility_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134jo_commercial_aerospace_decisive_event_registry_expansion_utility_audit_v1.json"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        self.security_master_dir = repo_root / "data" / "reference" / "security_master"
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_broader_symbol_pool_materialization_gap_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Report:
        utility = self._load_json(self.utility_path)
        registry_rows = self._load_csv(self.registry_path)
        symbol_pool_ids = {
            row["registry_id"]
            for row in utility["utility_rows"]
            if row["utility_class"] == "broader_symbol_pool_expander"
        }
        symbol_pool_rows = [row for row in registry_rows if row["registry_id"] in symbol_pool_ids]

        security_files = sorted(self.security_master_dir.glob("*.csv"))
        hit_rows: list[dict[str, Any]] = []
        total_hit_count = 0
        for security_file in security_files:
            rows = self._load_csv(security_file)
            hits = [row for row in rows if row["name"] in TARGET_NAMES]
            total_hit_count += len(hits)
            hit_rows.append(
                {
                    "security_master_file": security_file.name,
                    "row_count": str(len(rows)),
                    "target_hit_count": str(len(hits)),
                    "target_hits": "|".join(f"{row['symbol']}:{row['name']}" for row in hits) if hits else "none",
                }
            )

        extracted_candidate_total = sum(int(row["extracted_candidate_count"] or "0") for row in symbol_pool_rows)
        gap_rows = [
            {
                "gap_component": "broader_symbol_pool_expander_sources",
                "status": "candidate_names_present_but_not_normalized",
                "value": str(len(symbol_pool_rows)),
                "detail": f"extracted_candidate_total = {extracted_candidate_total}",
            },
            {
                "gap_component": "local_security_master_coverage",
                "status": "zero_target_name_hits",
                "value": str(total_hit_count),
                "detail": "none of the target symbol names referenced in retained broader-symbol-pool sources appear in the current local security-master inventory",
            },
            {
                "gap_component": "same_plane_symbol_pool_materialization",
                "status": "blocked_by_name_to_symbol_coverage_gap",
                "value": "0",
                "detail": "the branch is source-ready but cannot yet produce a normalized symbol pool from current local coverage",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(hit_rows[0].keys()))
            writer.writeheader()
            writer.writerows(hit_rows)

        summary = {
            "acceptance_posture": "freeze_v134jq_commercial_aerospace_broader_symbol_pool_materialization_gap_audit_v1",
            "broader_symbol_pool_expander_source_count": len(symbol_pool_rows),
            "broader_symbol_pool_extracted_candidate_total": extracted_candidate_total,
            "security_master_file_count": len(security_files),
            "security_master_target_hit_count": total_hit_count,
            "materialized_symbol_count": 0,
            "authoritative_gap": "name_to_symbol_coverage_gap",
            "gap_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_symbol_pool_materialization_gap_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JQ tries to turn the first live same-plane branch into a real broader symbol pool.",
            "It finds that the branch is source-ready but not yet materializable because the current local security-master coverage is too thin to normalize the candidate names carried by retained event sources.",
        ]
        return V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Report(
            summary=summary,
            gap_rows=gap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jq_commercial_aerospace_broader_symbol_pool_materialization_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
