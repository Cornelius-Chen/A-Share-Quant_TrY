import json
from pathlib import Path

from a_share_quant.strategy.v119a_cpo_xyz_false_positive_control_triage_v1 import main


def test_v119a_report_written() -> None:
    main()
    path = Path("reports/analysis/v119a_cpo_xyz_false_positive_control_triage_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["control_branch_status"] == "dead"
    assert payload["summary"]["parent_branch_status"] == "candidate_only"
