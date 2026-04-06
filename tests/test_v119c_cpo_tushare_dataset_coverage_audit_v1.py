import json
from pathlib import Path

from a_share_quant.strategy.v119c_cpo_tushare_dataset_coverage_audit_v1 import main


def test_v119c_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119c_cpo_tushare_dataset_coverage_audit_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["critical_daily_basic_ready"] is True
    assert payload["summary"]["critical_stk_limit_ready"] is True
