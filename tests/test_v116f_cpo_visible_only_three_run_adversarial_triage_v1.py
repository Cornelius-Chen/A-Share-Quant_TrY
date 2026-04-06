import json
from pathlib import Path


def test_v116f_triage_exists_and_blocks_promotion() -> None:
    report_path = Path("reports/analysis/v116f_cpo_visible_only_three_run_adversarial_triage_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116f_cpo_visible_only_three_run_adversarial_triage_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["retained_count"] >= 2
    assert payload["summary"]["blocked_count"] >= 1
    assert payload["summary"]["must_fix_next"]
