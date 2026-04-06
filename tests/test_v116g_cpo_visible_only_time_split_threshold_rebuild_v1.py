import json
from pathlib import Path


def test_v116g_time_split_report_exists() -> None:
    report_path = Path("reports/analysis/v116g_cpo_visible_only_time_split_threshold_rebuild_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116g_cpo_visible_only_time_split_threshold_rebuild_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["row_count"] >= 1
    assert len(payload["split_rows"]) >= 4
