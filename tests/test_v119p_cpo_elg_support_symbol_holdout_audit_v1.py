import json
from pathlib import Path

from a_share_quant.strategy.v119p_cpo_elg_support_symbol_holdout_audit_v1 import main


def test_v119p_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119p_cpo_elg_support_symbol_holdout_audit_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["evaluable_holdout_count"] >= 2
    assert payload["summary"]["min_evaluable_test_balanced_accuracy"] <= 0.5
