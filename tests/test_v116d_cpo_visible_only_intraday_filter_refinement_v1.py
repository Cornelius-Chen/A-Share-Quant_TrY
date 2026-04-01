import json
from pathlib import Path


def test_v116d_report_exists_and_has_variants() -> None:
    report_path = Path("reports/analysis/v116d_cpo_visible_only_intraday_filter_refinement_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116d_cpo_visible_only_intraday_filter_refinement_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["variant_count"] >= 10
    assert any(float(row["executed_order_count"]) > 0 for row in payload["variant_rows"])
    assert payload["summary"]["best_variant_by_equity"]
