import json
from pathlib import Path

from a_share_quant.strategy.v119o_cpo_lmn_three_run_adversarial_triage_v1 import main


def test_v119o_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119o_cpo_lmn_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["branch_status"] == "hard_candidate_non_replay_only"
    assert payload["summary"]["hard_candidate_allowed"] is True
    assert payload["summary"]["replay_facing_allowed"] is False
