import json
from pathlib import Path

from a_share_quant.strategy.v118u_cpo_sustained_participation_non_chase_external_audit_v1 import main


def test_v118u_report_written() -> None:
    main()
    path = Path("reports/analysis/v118u_cpo_sustained_participation_non_chase_external_audit_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["candidate_discriminator_name"] == "sustained_participation_non_chase_score_candidate"
    assert payload["summary"]["best_balanced_accuracy"] >= 0.0
