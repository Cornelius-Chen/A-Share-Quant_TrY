from pathlib import Path

from a_share_quant.strategy.v121a_cpo_participation_collapse_close_risk_discovery_v1 import (
    V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121a_cpo_participation_collapse_close_risk_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

