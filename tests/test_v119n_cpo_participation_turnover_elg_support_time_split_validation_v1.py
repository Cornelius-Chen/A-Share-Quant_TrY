import json
from pathlib import Path

from a_share_quant.strategy.v119n_cpo_participation_turnover_elg_support_time_split_validation_v1 import main


def test_v119n_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119n_cpo_participation_turnover_elg_support_time_split_validation_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["mean_test_balanced_accuracy"] >= 0.85
    assert payload["summary"]["min_test_balanced_accuracy"] >= 0.8
