import json
from pathlib import Path

from a_share_quant.strategy.v119d_cpo_tushare_turnover_discipline_discovery_v1 import main


def test_v119d_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119d_cpo_tushare_turnover_discipline_discovery_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["add_row_count"] == 16
    assert payload["summary"]["candidate_score_mean_gap_positive_minus_negative"] > 0
