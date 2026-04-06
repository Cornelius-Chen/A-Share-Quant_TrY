from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.data.tushare_bootstrap import (
    TushareUniverseBootstrapConfig,
    TushareUniverseBootstrapper,
)


@dataclass(slots=True)
class V124RCommercialAerospaceTushareFeedBootstrapReport:
    summary: dict[str, Any]
    output_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "output_rows": self.output_rows,
            "interpretation": self.interpretation,
        }


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124RCommercialAerospaceTushareFeedBootstrapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    config = TushareUniverseBootstrapConfig(
        start_date=date(2024, 1, 1),
        end_date=date.today(),
        universe_csv_path=repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv",
        raw_dir=repo_root / "data" / "raw",
        reference_dir=repo_root / "data" / "reference",
        pause_seconds=0.12,
        daily_filename="tushare_commercial_aerospace_daily_bars_v1.csv",
        daily_basic_filename="tushare_commercial_aerospace_daily_basic_v1.csv",
        moneyflow_filename="tushare_commercial_aerospace_moneyflow_v1.csv",
        stk_limit_filename="tushare_commercial_aerospace_stk_limit_v1.csv",
    )
    bootstrapper = TushareUniverseBootstrapper(config, repo_root=repo_root)
    outputs = bootstrapper.run()
    result = V124RCommercialAerospaceTushareFeedBootstrapReport(
        summary={
            "acceptance_posture": "freeze_v124r_commercial_aerospace_tushare_feed_bootstrap_v1",
            "provider": "tushare",
            "scope": "commercial_aerospace_merged_universe",
            "symbol_count": len(outputs["symbols"]),
            "start_date": config.start_date.isoformat(),
            "end_date": config.end_date.isoformat(),
            "daily_rows": outputs["daily_rows"],
            "daily_basic_rows": outputs["daily_basic_rows"],
            "moneyflow_rows": outputs["moneyflow_rows"],
            "stk_limit_rows": outputs["stk_limit_rows"],
        },
        output_rows=[
            {"dataset": "daily_bars", "path": str(outputs["daily_path"]), "row_count": outputs["daily_rows"]},
            {"dataset": "daily_basic", "path": str(outputs["daily_basic_path"]), "row_count": outputs["daily_basic_rows"]},
            {"dataset": "moneyflow", "path": str(outputs["moneyflow_path"]), "row_count": outputs["moneyflow_rows"]},
            {"dataset": "stk_limit", "path": str(outputs["stk_limit_path"]), "row_count": outputs["stk_limit_rows"]},
        ],
        interpretation=[
            "V1.24R bootstraps local Tushare feeds for the merged commercial aerospace universe rather than relying on web-only concept membership.",
            "This is the bridge from a broad A-share concept list to a machine-readable local support plane.",
            "Replay remains blocked until machine triage and control extraction are rebuilt on this wider supported set.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124r_commercial_aerospace_tushare_feed_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
