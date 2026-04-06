import json
from pathlib import Path

from a_share_quant.strategy.v118p_cpo_reclaim_absorption_external_audit_v1 import main


def test_v118p_report_written() -> None:
    main()
    path = Path("reports/analysis/v118p_cpo_reclaim_absorption_external_audit_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["candidate_discriminator_name"] == "reclaim_absorption_score_candidate"
    assert payload["summary"]["best_balanced_accuracy"] >= 0.0
    assert len(payload["threshold_audit_rows"]) >= 1
