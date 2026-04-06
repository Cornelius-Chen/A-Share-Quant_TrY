import json
from pathlib import Path

from a_share_quant.strategy.v123v_cpo_drawdown_control_priority_freeze_v1 import (
    V123VCpoDrawdownControlPriorityFreezeAnalyzer,
)


def test_v123v_freezes_control_priority_order() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123u_cpo_drawdown_risk_layer_attribution_matrix_v1.json").read_text(
            encoding="utf-8"
        )
    )
    result = V123VCpoDrawdownControlPriorityFreezeAnalyzer(repo_root=repo_root).analyze(v123u_payload=payload)
    assert result.summary["top_control_priority"] == "position_heat_guardrail"
    assert result.priority_rows[0]["control_layer"] == "position_heat_guardrail"
