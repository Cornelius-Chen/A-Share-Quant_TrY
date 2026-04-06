from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1 import (
    V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Report:
        audit = V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "board_local_event_attention_capital_handoff",
                "direction": "retain_as_frozen_read_only_input",
            },
            {
                "component": "market_snapshot_inventory_v6",
                "direction": "promote_as_first_broader_symbol_attention_search_surface",
            },
            {
                "component": "theme_snapshot_inventory_v7",
                "direction": "promote_as_first_broader_heat_proxy_expansion_surface",
            },
            {
                "component": "decisive_event_registry_v1",
                "direction": "promote_as_first_retained_event_source_expansion_surface",
            },
            {
                "component": "concept_purity_business_reference_layer",
                "direction": "keep_deferred_until_future_full_a_share_shift",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_during_inventory_stage",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jl_commercial_aerospace_jk_broader_attention_inventory_direction_triage_v1",
            "ready_local_broader_source_count": audit.summary["ready_local_broader_source_count"],
            "capital_true_selection_blocked": True,
            "authoritative_status": "retain_broader_attention_evidence_as_protocol_plus_inventory_open_and_fill_it_with_snapshots_and_retained_event_sources_before_any_promotion",
        }
        interpretation = [
            "V1.34JL converts the first broader-attention source inventory into direction.",
            "The next lawful move is to populate the frontier with broader symbol, heat-proxy, and retained-event evidence without promoting capital_true_selection or reopening deferred concept-purity work.",
        ]
        return V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jl_commercial_aerospace_jk_broader_attention_inventory_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
