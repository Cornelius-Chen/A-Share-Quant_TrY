import json
from pathlib import Path

from a_share_quant.strategy.v119r_cpo_elg_support_out_of_set_false_positive_audit_v1 import main


def test_v119r_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119r_cpo_elg_support_out_of_set_false_positive_audit_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["entry_leakage_rate"] > 0.3
    assert payload["summary"]["close_leakage_rate"] > 0.5
