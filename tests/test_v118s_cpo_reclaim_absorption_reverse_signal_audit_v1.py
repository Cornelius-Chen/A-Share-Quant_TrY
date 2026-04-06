import json
from pathlib import Path

from a_share_quant.strategy.v118s_cpo_reclaim_absorption_reverse_signal_audit_v1 import main


def test_v118s_report_written() -> None:
    main()
    path = Path("reports/analysis/v118s_cpo_reclaim_absorption_reverse_signal_audit_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "reverse_signal_status" in payload["summary"]
    assert payload["summary"]["best_balanced_accuracy"] >= 0.0
