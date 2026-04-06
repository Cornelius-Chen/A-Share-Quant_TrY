from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1 import (
    V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Report:
        audit = V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "000547",
                "direction": "retain_as_only_explicit_heat_anchor_seed_and_only_hard_anchor_decoy_counterpanel",
            },
            {
                "component": "603601",
                "direction": "retain_as_strongest_soft_heat_carrier_proxy_but_do_not_promote_to_hard_counterpanel_or_true_selection",
            },
            {
                "component": "002361_300342_301306",
                "direction": "retain_as_non_anchor_heat_proxies_with_different_local_roles",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_because_heat_proxy_clarity_does_not_equal_counterpanel_thickness",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134iz_commercial_aerospace_iy_heat_proxy_direction_triage_v1",
            "strongest_soft_heat_proxy_symbol": audit.summary["strongest_soft_heat_proxy_symbol"],
            "counterpanel_thickened": audit.summary["counterpanel_thickened"],
            "authoritative_status": "retain_board_local_heat_proxy_layer_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34IZ turns the new local heat-proxy layer into direction.",
            "The stack is allowed to become more articulate about local heat roles without pretending that role articulation solves the missing hard-evidence gaps.",
        ]
        return V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iz_commercial_aerospace_iy_heat_proxy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
