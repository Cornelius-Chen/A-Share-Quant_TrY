import json
from pathlib import Path

from a_share_quant.strategy.v118v_cpo_sustained_participation_non_chase_time_split_validation_v1 import main


def test_v118v_report_written() -> None:
    main()
    path = Path("reports/analysis/v118v_cpo_sustained_participation_non_chase_time_split_validation_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["split_count"] == 3
    assert len(payload["split_rows"]) == 3
