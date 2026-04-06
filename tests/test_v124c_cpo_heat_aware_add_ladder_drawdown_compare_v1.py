from pathlib import Path

from a_share_quant.strategy.v124b_cpo_heat_aware_add_ladder_audit_v1 import (
    V124BCpoHeatAwareAddLadderAuditAnalyzer,
)
from a_share_quant.strategy.v124b_cpo_heat_aware_add_ladder_audit_v1 import write_daily_state_csv, write_report
from a_share_quant.strategy.v124c_cpo_heat_aware_add_ladder_drawdown_compare_v1 import (
    V124CCpoHeatAwareAddLadderDrawdownCompareAnalyzer,
)


def test_v124c_heat_add_ladder_compare_has_three_intervals() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result_b, daily_rows = V124BCpoHeatAwareAddLadderAuditAnalyzer(repo_root=repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124b_cpo_heat_aware_add_ladder_audit_v1",
        result=result_b,
    )
    write_daily_state_csv(
        output_path=repo_root / "data" / "training" / "cpo_heat_aware_add_ladder_daily_state_v1.csv",
        rows=daily_rows,
    )
    result = V124CCpoHeatAwareAddLadderDrawdownCompareAnalyzer(repo_root=repo_root).analyze()

    assert len(result.interval_rows) == 3
    assert result.summary["best_ladder_variant_name"]
