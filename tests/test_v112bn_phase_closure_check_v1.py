import json
from pathlib import Path


def test_v112bn_phase_closure_check_closes_successfully() -> None:
    payload = json.loads(Path("reports/analysis/v112bn_phase_closure_check_v1.json").read_text(encoding="utf-8"))
    assert payload["summary"]["v112bn_success_criteria_met"] is True
    assert payload["summary"]["formal_training_now"] is False
    assert payload["summary"]["formal_signal_generation_now"] is False
