from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.data.tushare_bootstrap import (
    TushareCpoBootstrapConfig,
    TushareCpoBootstrapper,
)


@dataclass(slots=True)
class V119BCpoTushareDataBootstrapReport:
    summary: dict[str, Any]
    output_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "output_rows": self.output_rows,
            "interpretation": self.interpretation,
        }


def write_report(*, reports_dir: Path, report_name: str, result: V119BCpoTushareDataBootstrapReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    config = TushareCpoBootstrapConfig(
        start_date=date(2023, 1, 1),
        end_date=date.today(),
        cohort_report_path=repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json",
        raw_dir=repo_root / "data" / "raw",
        reference_dir=repo_root / "data" / "reference",
        pause_seconds=0.12,
        daily_basic_filename="tushare_cpo_daily_basic_v1.csv",
        moneyflow_filename="tushare_cpo_moneyflow_v1.csv",
        stk_limit_filename="tushare_cpo_stk_limit_v1.csv",
    )
    bootstrapper = TushareCpoBootstrapper(config, repo_root=repo_root)
    outputs = bootstrapper.run()
    result = V119BCpoTushareDataBootstrapReport(
        summary={
            "acceptance_posture": "freeze_v119b_cpo_tushare_data_bootstrap_v1",
            "provider": "tushare",
            "scope": "cpo_bounded_cohort",
            "symbol_count": len(outputs["symbols"]),
            "start_date": config.start_date.isoformat(),
            "end_date": config.end_date.isoformat(),
            "daily_basic_rows": outputs["daily_basic_rows"],
            "moneyflow_rows": outputs["moneyflow_rows"],
            "stk_limit_rows": outputs["stk_limit_rows"],
        },
        output_rows=[
            {"dataset": "daily_basic", "path": str(outputs["daily_basic_path"]), "row_count": outputs["daily_basic_rows"]},
            {"dataset": "moneyflow", "path": str(outputs["moneyflow_path"]), "row_count": outputs["moneyflow_rows"]},
            {"dataset": "stk_limit", "path": str(outputs["stk_limit_path"]), "row_count": outputs["stk_limit_rows"]},
        ],
        interpretation=[
            "V1.19B bootstraps the first Tushare-backed CPO data pack using the bounded cohort universe from V112AA.",
            "The purpose is to replace proxy free-float and turnover context with direct Tushare daily_basic fields, while also pulling moneyflow and daily price-limit references.",
            "This is a data-layer completion step, not a new trading branch.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119b_cpo_tushare_data_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
