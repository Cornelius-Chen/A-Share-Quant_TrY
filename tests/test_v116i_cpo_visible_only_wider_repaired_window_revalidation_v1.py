import json
from pathlib import Path


def test_v116i_wider_revalidation_exists() -> None:
    report_path = Path("reports/analysis/v116i_cpo_visible_only_wider_repaired_window_revalidation_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116i_cpo_visible_only_wider_repaired_window_revalidation_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["wider_window_day_count"] >= 1
    assert len(payload["variant_rows"]) == 2
