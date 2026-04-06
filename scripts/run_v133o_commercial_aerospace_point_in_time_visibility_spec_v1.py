from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v133o_commercial_aerospace_point_in_time_visibility_spec_v1 import (
    V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133o_commercial_aerospace_point_in_time_visibility_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
