from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Report:
    summary: dict[str, Any]
    spec_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "spec_rows": self.spec_rows,
            "interpretation": self.interpretation,
        }


class V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.holdings_audit_path = (
            repo_root / "reports" / "analysis" / "v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_start_of_day_sell_binding_surface_spec_v1.csv"
        )

    def analyze(self) -> V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Report:
        holdings_audit = json.loads(self.holdings_audit_path.read_text(encoding="utf-8"))

        spec_rows = [
            {
                "surface_component": "start_of_day_holdings_ledger",
                "status": "must_build",
                "definition": "per symbol, per trade_date quantity carried into the open from the frozen EOD primary",
                "why_it_exists": "intraday sell binding must know real inventory before any same-day open/add/reduce happens",
            },
            {
                "surface_component": "eligible_intraday_sell_quantity",
                "status": "must_build",
                "definition": "sellable quantity starts equal to start_of_day_holdings_ledger and can only decrease intraday",
                "why_it_exists": "prevents the sell lane from liquidating same-day opens or same-day adds that were never in opening inventory",
            },
            {
                "surface_component": "same_day_new_lots_bucket",
                "status": "must_build",
                "definition": "same-day open/add quantity is tracked separately and is not eligible for intraday sell binding on that day",
                "why_it_exists": "keeps intraday sell binding aligned with actual held-over inventory rather than newly-created lots",
            },
            {
                "surface_component": "sell_consumption_ledger",
                "status": "must_build",
                "definition": "each intraday sell event consumes remaining eligible sell quantity in trigger-time order",
                "why_it_exists": "turns minute shadow sells into quantity-aware state transitions",
            },
            {
                "surface_component": "end_of_day_residual_bridge",
                "status": "must_build",
                "definition": "maps remaining eligible quantity and same-day new lots back into the frozen primary after market close",
                "why_it_exists": "lets the sell-side lane stay read-only during the day while still reconciling against the primary state boundary",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(spec_rows[0].keys()))
            writer.writeheader()
            writer.writerows(spec_rows)

        summary = {
            "acceptance_posture": "freeze_v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1",
            "broader_hit_session_count": holdings_audit["summary"]["broader_hit_session_count"],
            "fully_funded_overlap_count": holdings_audit["summary"]["fully_funded_overlap_count"],
            "must_build_component_count": len(spec_rows),
            "spec_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_start_of_day_sell_binding_surface_spec_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BW turns the holdings-aware gap into a concrete start-of-day sell binding surface specification.",
            "The key idea is that intraday sell binding may only consume carried inventory, while same-day new lots stay in a separate bucket.",
        ]
        return V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Report(
            summary=summary,
            spec_rows=spec_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
