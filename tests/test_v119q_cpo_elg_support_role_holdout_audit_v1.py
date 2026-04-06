import json
from pathlib import Path

from a_share_quant.strategy.v119q_cpo_elg_support_role_holdout_audit_v1 import main


def test_v119q_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119q_cpo_elg_support_role_holdout_audit_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["evaluable_holdout_count"] >= 1
    assert payload["summary"]["min_evaluable_test_balanced_accuracy"] <= 0.55
