import json
from pathlib import Path

from a_share_quant.strategy.v119h_cpo_participation_turnover_combo_discovery_v1 import main as run_v119h
from a_share_quant.strategy.v119i_cpo_participation_turnover_combo_external_audit_v1 import main


def test_v119i_report_written() -> None:
    run_v119h()
    main()
    payload = json.loads(
        Path("reports/analysis/v119i_cpo_participation_turnover_combo_external_audit_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["best_balanced_accuracy"] >= 0.85
