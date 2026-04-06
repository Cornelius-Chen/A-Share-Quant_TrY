import json
from pathlib import Path

from a_share_quant.strategy.v119k_cpo_hij_three_run_adversarial_triage_v1 import main


def test_v119k_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119k_cpo_hij_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["branch_status"] == "candidate_only"
    assert payload["summary"]["replay_facing_allowed"] is False
    assert payload["summary"]["candidate_only_allowed"] is True
