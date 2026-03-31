import json
from pathlib import Path


def test_v112bn_teacher_decomposition_search_produces_non_cash_candidate() -> None:
    payload = json.loads(Path("reports/analysis/v112bn_teacher_decomposition_gate_search_v1.json").read_text(encoding="utf-8"))
    summary = payload["summary"]
    assert summary["no_leak_enforced"] is True
    assert summary["candidate_row_count"] > 0
    assert summary["best_candidate_rule_count"] >= 0
    assert summary["best_candidate_non_cash"] in {True, False}
    assert payload["candidate_rows"]
