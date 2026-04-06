from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)
from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _ReplayConfig,
)


@dataclass(slots=True)
class V127KCommercialAerospaceChronicDragSymbolVetoAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.v127g_path = repo_root / "reports" / "analysis" / "v127g_commercial_aerospace_primary_reference_attribution_v1.json"

    def _drag_symbols(self) -> list[str]:
        payload = json.loads(self.v127g_path.read_text(encoding="utf-8"))
        primary_rows = [row for row in payload["symbol_attribution_rows"] if row["variant"] == "v127e_broad_half_reference"]
        return [row["symbol"] for row in sorted(primary_rows, key=lambda item: item["total_pnl"])[:3]]

    def _simulate_with_veto(self, veto_symbols: set[str], name: str) -> dict[str, Any]:
        base = self.helper._load_base_config()
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self.helper._split_rows(label_table.training_rows)
        config = _ReplayConfig(
            name=name,
            preheat_cap=int(base["preheat_cap"]),
            impulse_cap=int(base["impulse_cap"]),
            cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
            min_increment_notional=float(base["min_increment_notional"]),
            preheat_full_target_notional=70_000.0,
            family="broad_half_reference",
            sell_ratio=0.5,
        )

        filtered_rows = [row for row in rows if row["symbol"] not in veto_symbols]
        return self.helper._simulate_variant_detailed(filtered_rows, test_dates, date_to_idx, config)

    def analyze(self) -> V127KCommercialAerospaceChronicDragSymbolVetoAuditReport:
        drag_symbols = self._drag_symbols()
        reference = self._simulate_with_veto(set(), "broad_half_reference")
        veto_1 = self._simulate_with_veto({drag_symbols[0]}, f"veto_{drag_symbols[0]}")
        veto_2 = self._simulate_with_veto(set(drag_symbols[:2]), f"veto_{drag_symbols[0]}_{drag_symbols[1]}")
        veto_3 = self._simulate_with_veto(set(drag_symbols[:3]), f"veto_{drag_symbols[0]}_{drag_symbols[1]}_{drag_symbols[2]}")
        variant_rows = [
            {
                "variant": reference["variant"],
                "veto_symbols": [],
                **reference["summary"],
            },
            {
                "variant": veto_1["variant"],
                "veto_symbols": drag_symbols[:1],
                **veto_1["summary"],
            },
            {
                "variant": veto_2["variant"],
                "veto_symbols": drag_symbols[:2],
                **veto_2["summary"],
            },
            {
                "variant": veto_3["variant"],
                "veto_symbols": drag_symbols[:3],
                **veto_3["summary"],
            },
        ]
        best_variant = min(variant_rows, key=lambda row: (row["max_drawdown"], -row["final_equity"]))
        summary = {
            "acceptance_posture": "freeze_v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1",
            "reference_variant": "broad_half_reference",
            "reference_final_equity": reference["summary"]["final_equity"],
            "reference_max_drawdown": reference["summary"]["max_drawdown"],
            "drag_symbols_ranked": drag_symbols,
            "best_variant": best_variant["variant"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
        }
        interpretation = [
            "V1.27K tests the simplest attribution-driven next step after the de-risk budget stopline: remove chronic drag symbols from the primary replay and see if the frontier improves.",
            "This is not a new family; it is a symbol-level veto audit derived directly from the attribution surface.",
        ]
        return V127KCommercialAerospaceChronicDragSymbolVetoAuditReport(summary=summary, variant_rows=variant_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V127KCommercialAerospaceChronicDragSymbolVetoAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
