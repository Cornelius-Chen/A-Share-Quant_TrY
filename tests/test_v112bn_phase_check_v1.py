import json
from pathlib import Path


def test_v112bn_phase_check_accepts_report_only_search() -> None:
    payload = json.loads(Path("reports/analysis/v112bn_phase_check_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["do_open_v112bn_now"] is True
    assert payload["summary"]["candidate_row_count"] > 0
