import json
from pathlib import Path

from a_share_quant.strategy.v118x_cpo_sustained_participation_false_positive_control_discovery_v1 import main


def test_v118x_report_written() -> None:
    main()
    path = Path("reports/analysis/v118x_cpo_sustained_participation_false_positive_control_discovery_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "control_helpful" in payload["summary"]
    assert payload["summary"]["row_count"] >= 1
