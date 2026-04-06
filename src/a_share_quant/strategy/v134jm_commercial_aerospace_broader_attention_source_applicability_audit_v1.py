from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CURRENT_FRONTIER_SYMBOLS = (
    "000547",
    "002361",
    "300342",
    "301306",
    "603601",
    "000738",
    "600118",
    "002085",
)


@dataclass(slots=True)
class V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Report:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.analysis_dir = repo_root / "reports" / "analysis"
        self.inventory_path = (
            self.analysis_dir / "v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1.json"
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
            / "commercial_aerospace_broader_attention_source_applicability_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Report:
        inventory = self._load_json(self.inventory_path)
        market_rows = self._load_csv(self.market_snapshot_path)
        theme_rows = self._load_csv(self.theme_snapshot_path)
        decisive_rows = self._load_csv(self.decisive_registry_path)

        market_symbols = {row["symbol"] for row in market_rows}
        theme_symbols = {row["symbol"] for row in theme_rows}
        frontier_symbols = set(CURRENT_FRONTIER_SYMBOLS)

        market_overlap = sorted(frontier_symbols & market_symbols)
        theme_overlap = sorted(frontier_symbols & theme_symbols)

        market_first_date = market_rows[0]["trade_date"]
        market_last_date = market_rows[-1]["trade_date"]
        theme_first_date = theme_rows[0]["trade_date"]
        theme_last_date = theme_rows[-1]["trade_date"]
        decisive_first_time = decisive_rows[0]["public_release_time"]
        decisive_last_time = decisive_rows[-1]["public_release_time"]

        source_rows = [
            {
                "source_component": "market_snapshot_inventory_v6",
                "temporal_alignment": "misaligned_2024_only",
                "frontier_symbol_overlap_count": str(len(market_overlap)),
                "frontier_symbol_overlap": "|".join(market_overlap),
                "same_plane_applicability": "structural_prior_only_not_same_plane_live_evidence",
                "detail": f"coverage = {market_first_date} -> {market_last_date}",
            },
            {
                "source_component": "theme_snapshot_inventory_v7",
                "temporal_alignment": "misaligned_2024_only",
                "frontier_symbol_overlap_count": str(len(theme_overlap)),
                "frontier_symbol_overlap": "|".join(theme_overlap) if theme_overlap else "none",
                "same_plane_applicability": "theme_structure_prior_only_not_same_plane_live_evidence",
                "detail": f"coverage = {theme_first_date} -> {theme_last_date}",
            },
            {
                "source_component": "decisive_event_registry_v1",
                "temporal_alignment": "aligned_2026_event_surface",
                "frontier_symbol_overlap_count": "n/a",
                "frontier_symbol_overlap": "n/a",
                "same_plane_applicability": "first_live_same_plane_expansion_source",
                "detail": f"coverage = {decisive_first_time} -> {decisive_last_time}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
            writer.writeheader()
            writer.writerows(source_rows)

        summary = {
            "acceptance_posture": "freeze_v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1",
            "inventory_frontier_state": inventory["summary"]["frontier_state"],
            "current_frontier_symbol_count": len(frontier_symbols),
            "market_snapshot_overlap_count": len(market_overlap),
            "theme_snapshot_overlap_count": len(theme_overlap),
            "market_snapshot_temporal_alignment": "misaligned_2024_only",
            "theme_snapshot_temporal_alignment": "misaligned_2024_only",
            "decisive_registry_temporal_alignment": "aligned_2026_event_surface",
            "same_plane_ready_source_count": 1,
            "structural_prior_only_source_count": 2,
            "applicability_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_broader_attention_source_applicability_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JM asks whether the newly inventoried broader-attention sources are actually usable on the same temporal plane as the current 2026 commercial-aerospace route.",
            "The answer is asymmetric: the decisive event registry is same-plane ready, while the snapshot inventories are still useful only as structural priors because they stop in 2024.",
        ]
        return V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Report(
            summary=summary,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
