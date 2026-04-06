import json
from pathlib import Path


def test_v116e_candidate_audit_exists_and_names_candidates() -> None:
    report_path = Path("reports/analysis/v116e_cpo_visible_only_candidate_audit_v1.json")
    if not report_path.exists():
        from a_share_quant.strategy.v116e_cpo_visible_only_candidate_audit_v1 import main

        main()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["variant_count"] >= 4
    assert payload["summary"]["cleanest_executing_candidate"]
    assert payload["summary"]["most_expressive_non_ceiling_candidate"]
