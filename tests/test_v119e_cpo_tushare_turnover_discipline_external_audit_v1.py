import json
from pathlib import Path

from a_share_quant.strategy.v119d_cpo_tushare_turnover_discipline_discovery_v1 import main as run_v119d
from a_share_quant.strategy.v119e_cpo_tushare_turnover_discipline_external_audit_v1 import main


def test_v119e_report_written() -> None:
    run_v119d()
    main()
    payload = json.loads(
        Path("reports/analysis/v119e_cpo_tushare_turnover_discipline_external_audit_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["external_pool_signal_clear"] is True
    assert payload["summary"]["best_balanced_accuracy"] >= 0.8
