from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113r_cpo_full_board_daily_bar_proxy_completion_v1 import (
    V113RCPOFullBoardDailyBarProxyCompletionAnalyzer,
    load_json_report,
    write_v113r_cpo_full_board_daily_bar_proxy_completion_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113RCPOFullBoardDailyBarProxyCompletionAnalyzer()
    result = analyzer.analyze(
        repo_root=repo_root,
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
    )
    output_path = write_v113r_cpo_full_board_daily_bar_proxy_completion_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113r_cpo_full_board_daily_bar_proxy_completion_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
