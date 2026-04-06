import json
from pathlib import Path

from a_share_quant.strategy.v118y_cpo_sustained_participation_false_positive_control_external_audit_v1 import main


def test_v118y_report_written() -> None:
    main()
    path = Path("reports/analysis/v118y_cpo_sustained_participation_false_positive_control_external_audit_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["best_balanced_accuracy"] >= 0.0
