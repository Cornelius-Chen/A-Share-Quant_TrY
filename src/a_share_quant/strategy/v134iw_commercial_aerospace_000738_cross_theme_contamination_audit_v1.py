from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMPARATOR_SYMBOLS = {
    "002353": "杰瑞股份",
    "600875": "东方电气",
}


@dataclass(slots=True)
class V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_000738_cross_theme_contamination_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Report:
        outside_watch = self._load_json(
            "reports/analysis/v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1.json"
        )
        universe_triage_rows = list(
            csv.DictReader(
                (self.repo_root / "data" / "training" / "commercial_aerospace_universe_triage_v1.csv").open(
                    encoding="utf-8-sig"
                )
            )
        )
        broader_snapshots_rows = list(
            csv.DictReader(
                (
                    self.repo_root
                    / "data"
                    / "derived"
                    / "stock_snapshots"
                    / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
                ).open(encoding="utf-8-sig")
            )
        )
        broader_manifest = (
            self.repo_root / "config" / "market_research_v6_catalyst_supported_carry_persistence_refresh_manifest.yaml"
        ).read_text(encoding="utf-8")
        commercial_daily_symbols = {
            row["symbol"]
            for row in csv.DictReader(
                (
                    self.repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
                ).open(encoding="utf-8-sig")
            )
        }

        watch_row = next(row for row in outside_watch["supervision_rows"] if row["symbol"] == "000738")
        triage_000738 = next(row for row in universe_triage_rows if row["symbol"] == "000738")
        broader_000738 = [row for row in broader_snapshots_rows if row["symbol"] == "000738"]
        broader_sector_names = sorted({row["sector_name"] for row in broader_000738})
        broader_context_mode = "multi_day_reinforcement" if 'symbol: "000738"' in broader_manifest else ""

        symbol_rows = [
            {
                "symbol": "000738",
                "display_name": "航发控制",
                "commercial_aerospace_local_status": watch_row["supervision_role"],
                "commercial_aerospace_subgroup": triage_000738["subgroup"],
                "commercial_aerospace_machine_semantic": triage_000738["machine_semantic"],
                "broader_market_context_mode": broader_context_mode,
                "broader_sector_names": "|".join(broader_sector_names),
                "theme_purity_label": "cross_theme_contaminated_watch",
                "future_labeling_requirement": "add_concept_purity_and_basic_business_reference_before_using_as_clean_carrier_evidence",
                "learning_reading": "000738 remains a useful local watch, but broader market metadata frames it as a defense/aerospace multi-day reinforcement name rather than as a clean commercial-aerospace-only carrier",
            }
        ]

        for symbol, display_name in COMPARATOR_SYMBOLS.items():
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "display_name": display_name,
                    "commercial_aerospace_local_status": "not_present_in_current_commercial_aerospace_surface",
                    "commercial_aerospace_subgroup": "",
                    "commercial_aerospace_machine_semantic": "",
                    "broader_market_context_mode": "",
                    "broader_sector_names": "",
                    "theme_purity_label": "cross_theme_comparator_missing_from_current_local_surface",
                    "future_labeling_requirement": "wider_same_plane_data_scope_needed_before_using_as_gas_turbine_purity_comparator",
                    "learning_reading": "this comparator may matter for a gas-turbine contamination hypothesis, but it is absent from the current commercial-aerospace local surface and therefore cannot yet be used in same-plane local board supervision without widening the data scope",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        comparator_absent_count = sum(1 for symbol in COMPARATOR_SYMBOLS if symbol not in commercial_daily_symbols)
        summary = {
            "acceptance_posture": "freeze_v134iw_commercial_aerospace_000738_cross_theme_contamination_audit_v1",
            "primary_symbol": "000738",
            "theme_purity_label": "cross_theme_contaminated_watch",
            "comparator_absent_count": comparator_absent_count,
            "broader_context_mode": broader_context_mode,
            "theme_contamination_csv": str(self.output_csv.relative_to(self.repo_root)),
            "future_labeling_extension": "concept_purity_plus_basic_business_reference_layer",
            "authoritative_rule": "000738 should no longer be read as a clean commercial-aerospace-only second-carrier watch: its current evidence is cross-theme contaminated, and the proposed gas-turbine comparators are not present in the current local commercial-aerospace surface",
        }
        interpretation = [
            "V1.34IW records the user-raised contamination risk instead of treating 000738 as a clean same-theme candidate.",
            "The audit stays honest about scope: 000738 can be downshifted to a contaminated watch now, but same-plane comparator work with gas-turbine names still requires wider local data coverage.",
            "The downstream labeling implication is explicit: future supervision should carry a concept-purity and basic-business reference layer before cross-theme names are promoted into board-specific carrier evidence.",
        ]
        return V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iw_commercial_aerospace_000738_cross_theme_contamination_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
