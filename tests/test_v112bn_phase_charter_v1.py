import json
from pathlib import Path


def test_v112bn_phase_charter_requires_prior_closures() -> None:
    payload = json.loads(Path("reports/analysis/v112bn_phase_charter_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["do_open_v112bn_now"] is True
    assert "brute-force decomposing its gate" in payload["charter"]["mission"]
