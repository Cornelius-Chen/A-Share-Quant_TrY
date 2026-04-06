from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Report:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.analysis_dir = repo_root / "reports" / "analysis"
        self.frontier_opening_path = (
            self.analysis_dir / "v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1.json"
        )
        self.local_handoff_path = (
            self.analysis_dir / "v134jg_commercial_aerospace_event_attention_capital_local_handoff_package_v1.json"
        )
        self.market_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.theme_snapshot_path = (
            repo_root / "data" / "derived" / "stock_snapshots" / "theme_research_stock_snapshots_v7.csv"
        )
        self.decisive_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_broader_attention_evidence_source_inventory_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Report:
        frontier_opening = self._load_json(self.frontier_opening_path)
        local_handoff = self._load_json(self.local_handoff_path)
        market_snapshot_rows = self._load_csv(self.market_snapshot_path)
        theme_snapshot_rows = self._load_csv(self.theme_snapshot_path)
        decisive_registry_rows = self._load_csv(self.decisive_registry_path)

        retained_event_count = sum(row["decisive_retained"] == "True" for row in decisive_registry_rows)
        turning_point_watch_count = sum(
            row["decisive_semantic"] == "turning_point_watch" for row in decisive_registry_rows
        )
        layer_counts: dict[str, int] = {}
        for row in decisive_registry_rows:
            layer = row["layer"]
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        source_rows = [
            {
                "source_component": "board_local_event_attention_capital_handoff",
                "source_status": "frozen_read_only_input",
                "source_scope": "board_local_supervision",
                "row_count": "n/a",
                "retained_count": "n/a",
                "readiness": "ready_as_frozen_input",
                "detail": local_handoff["package_rows"][0]["detail"],
            },
            {
                "source_component": "market_snapshot_inventory_v6",
                "source_status": "available_local_broader_symbol_surface",
                "source_scope": "broader_symbol_attention_search",
                "row_count": str(len(market_snapshot_rows)),
                "retained_count": str(len(market_snapshot_rows)),
                "readiness": "ready_for_broader_attention_supervision",
                "detail": "market-wide snapshot surface with concept, liquidity, resonance, and sector context fields",
            },
            {
                "source_component": "theme_snapshot_inventory_v7",
                "source_status": "available_local_broader_theme_surface",
                "source_scope": "broader_heat_proxy_expansion",
                "row_count": str(len(theme_snapshot_rows)),
                "retained_count": str(len(theme_snapshot_rows)),
                "readiness": "ready_for_broader_attention_supervision",
                "detail": "theme-level snapshot surface suitable for local heat and role proxy expansion",
            },
            {
                "source_component": "decisive_event_registry_v1",
                "source_status": "available_local_event_source_surface",
                "source_scope": "retained_symbol_source_and_event_alignment_expansion",
                "row_count": str(len(decisive_registry_rows)),
                "retained_count": str(retained_event_count),
                "readiness": "ready_for_broader_event_attention_supervision",
                "detail": (
                    f"retained_event_count = {retained_event_count}; "
                    f"turning_point_watch_count = {turning_point_watch_count}; "
                    f"layer_counts = {layer_counts}"
                ),
            },
            {
                "source_component": "concept_purity_business_reference_layer",
                "source_status": "deferred_not_in_current_local_inventory",
                "source_scope": "future_cross_theme_and_basic_business_validation",
                "row_count": "0",
                "retained_count": "0",
                "readiness": "deferred_until_future_full_a_share_coverage",
                "detail": "user explicitly deferred broader concept-purity and business-reference integration until fuller A-share information exists",
            },
            {
                "source_component": "capital_true_selection_promotion",
                "source_status": "blocked_downstream_consumer",
                "source_scope": "future_only",
                "row_count": "0",
                "retained_count": "0",
                "readiness": "still_blocked",
                "detail": "inventory readiness does not authorize promotion; it only opens the evidence frontier",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
            writer.writeheader()
            writer.writerows(source_rows)

        summary = {
            "acceptance_posture": "freeze_v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1",
            "frontier_name": frontier_opening["summary"]["frontier_name"],
            "frontier_state": frontier_opening["summary"]["frontier_state"],
            "frozen_input_count": 1,
            "ready_local_broader_source_count": 3,
            "deferred_source_count": 1,
            "blocked_consumer_count": 1,
            "market_snapshot_row_count": len(market_snapshot_rows),
            "theme_snapshot_row_count": len(theme_snapshot_rows),
            "decisive_registry_row_count": len(decisive_registry_rows),
            "decisive_registry_retained_count": retained_event_count,
            "inventory_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_attention_evidence_source_inventory_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JK is the first concrete inventory surface under the broader_attention_evidence frontier.",
            "It shows that the frontier is not empty: broader snapshot surfaces and retained event-source registry are already locally available, while concept-purity and business-reference expansion remain intentionally deferred.",
        ]
        return V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Report(
            summary=summary,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
