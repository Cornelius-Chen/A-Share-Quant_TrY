import json
from pathlib import Path

from a_share_quant.strategy.v118o_cpo_reclaim_absorption_discovery_v1 import main


def test_v118o_report_written() -> None:
    main()
    path = Path("reports/analysis/v118o_cpo_reclaim_absorption_discovery_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["candidate_discriminator_name"] == "reclaim_absorption_score_candidate"
    assert payload["summary"]["add_row_count"] >= 1
    assert len(payload["candidate_score_rows"]) == payload["summary"]["add_row_count"]
