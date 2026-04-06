import json
from pathlib import Path

from a_share_quant.strategy.v119d_cpo_tushare_turnover_discipline_discovery_v1 import main as run_v119d
from a_share_quant.strategy.v119e_cpo_tushare_turnover_discipline_external_audit_v1 import main as run_v119e
from a_share_quant.strategy.v119f_cpo_tushare_turnover_discipline_time_split_validation_v1 import main


def test_v119f_report_written() -> None:
    run_v119d()
    run_v119e()
    main()
    payload = json.loads(
        Path("reports/analysis/v119f_cpo_tushare_turnover_discipline_time_split_validation_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["mean_test_balanced_accuracy"] >= 0.7
    assert payload["summary"]["min_test_balanced_accuracy"] >= 0.5
