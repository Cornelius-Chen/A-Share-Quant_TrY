import json
from pathlib import Path

from a_share_quant.strategy.v119l_cpo_participation_turnover_elg_support_discovery_v1 import main


def test_v119l_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119l_cpo_participation_turnover_elg_support_discovery_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["candidate_discriminator_name"] == "participation_turnover_elg_support_score_candidate"
    assert payload["summary"]["candidate_score_mean_gap_positive_minus_negative"] > 1.8
