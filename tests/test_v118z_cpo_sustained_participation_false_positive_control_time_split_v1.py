import json
from pathlib import Path

from a_share_quant.strategy.v118z_cpo_sustained_participation_false_positive_control_time_split_v1 import main


def test_v118z_report_written() -> None:
    main()
    path = Path("reports/analysis/v118z_cpo_sustained_participation_false_positive_control_time_split_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["split_count"] == 3
