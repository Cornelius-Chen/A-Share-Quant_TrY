import json
from pathlib import Path

from a_share_quant.strategy.v118r_cpo_opq_three_run_adversarial_triage_v1 import main


def test_v118r_report_written() -> None:
    main()
    path = Path("reports/analysis/v118r_cpo_opq_three_run_adversarial_triage_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["branch_status"] == "dead"
    assert payload["summary"]["soft_expectancy_component_allowed"] is False
