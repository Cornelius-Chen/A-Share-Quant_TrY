import json
from pathlib import Path

from a_share_quant.strategy.v119t_cpo_same_family_deentangling_scan_v1 import main


def test_v119t_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119t_cpo_same_family_deentangling_scan_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["variant_count"] >= 4
    assert payload["summary"]["best_symbol_holdout_variant"] == "symbol_date_blend_033"
