import json
from pathlib import Path

from a_share_quant.strategy.v119s_cpo_pqr_three_run_adversarial_triage_v1 import main


def test_v119s_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119s_cpo_pqr_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["branch_status"] == "candidate_only"
    assert payload["summary"]["hard_candidate_allowed"] is False
    assert payload["summary"]["replay_facing_allowed"] is False
