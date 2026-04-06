import json
from pathlib import Path

from a_share_quant.strategy.v119u_cpo_same_family_deentangling_stopline_v1 import main


def test_v119u_report_written() -> None:
    main()
    payload = json.loads(Path("reports/analysis/v119u_cpo_same_family_deentangling_stopline_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["same_family_micro_tuning_allowed"] is False
