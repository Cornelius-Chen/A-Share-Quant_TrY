from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v118n_cpo_klm_soft_component_triage_v1 import (
    V118NCpoKlmSoftComponentTriageAnalyzer,
)


def test_v118n_klm_soft_component_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V118NCpoKlmSoftComponentTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118k_payload=json.loads((repo_root / "reports" / "analysis" / "v118k_cpo_breakout_damage_soft_component_integration_review_v1.json").read_text(encoding="utf-8")),
        v118l_payload=json.loads((repo_root / "reports" / "analysis" / "v118l_cpo_breakout_damage_soft_component_external_audit_v1.json").read_text(encoding="utf-8")),
        v118m_payload=json.loads((repo_root / "reports" / "analysis" / "v118m_cpo_breakout_damage_soft_component_time_split_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["breakout_damage_soft_component_status"] == "archived_soft_component"
    assert result.summary["active_integration_allowed"] is False
    assert len(result.triage_rows) == 4
