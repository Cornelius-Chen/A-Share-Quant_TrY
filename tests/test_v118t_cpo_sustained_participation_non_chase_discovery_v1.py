import json
from pathlib import Path

from a_share_quant.strategy.v118t_cpo_sustained_participation_non_chase_discovery_v1 import main


def test_v118t_report_written() -> None:
    main()
    path = Path("reports/analysis/v118t_cpo_sustained_participation_non_chase_discovery_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["candidate_discriminator_name"] == "sustained_participation_non_chase_score_candidate"
    assert payload["summary"]["add_row_count"] >= 1
