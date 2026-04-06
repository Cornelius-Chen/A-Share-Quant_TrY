import json
from pathlib import Path


def test_v116h_alignment_report_exists_and_confirms_strict_after() -> None:
    report_path = Path("reports/analysis/v116h_cpo_checkpoint_to_fill_alignment_audit_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116h_cpo_checkpoint_to_fill_alignment_audit_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["row_count"] >= 1
    assert payload["summary"]["strict_alignment_confirmed"] is True
