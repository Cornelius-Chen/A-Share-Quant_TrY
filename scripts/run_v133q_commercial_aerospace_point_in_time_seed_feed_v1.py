from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v133q_commercial_aerospace_point_in_time_seed_feed_v1 import (
    V133QCommercialAerospacePointInTimeSeedFeedAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133QCommercialAerospacePointInTimeSeedFeedAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133q_commercial_aerospace_point_in_time_seed_feed_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
