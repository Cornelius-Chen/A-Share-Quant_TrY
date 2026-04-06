import json
from pathlib import Path

from a_share_quant.strategy.v119h_cpo_participation_turnover_combo_discovery_v1 import main as run_v119h
from a_share_quant.strategy.v119i_cpo_participation_turnover_combo_external_audit_v1 import main as run_v119i
from a_share_quant.strategy.v119j_cpo_participation_turnover_combo_time_split_validation_v1 import main


def test_v119j_report_written() -> None:
    run_v119h()
    run_v119i()
    main()
    payload = json.loads(
        Path("reports/analysis/v119j_cpo_participation_turnover_combo_time_split_validation_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["mean_test_balanced_accuracy"] >= 0.79
    assert payload["summary"]["min_test_balanced_accuracy"] >= 0.6
