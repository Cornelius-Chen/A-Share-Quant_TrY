import json
from pathlib import Path

from a_share_quant.strategy.v118w_cpo_tuv_three_run_adversarial_triage_v1 import main


def test_v118w_report_written() -> None:
    main()
    path = Path("reports/analysis/v118w_cpo_tuv_three_run_adversarial_triage_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["branch_status"] == "candidate_only"
    assert payload["summary"]["candidate_only_allowed"] is True
