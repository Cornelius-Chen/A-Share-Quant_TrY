from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v119v_cpo_limit_discipline_support_discovery_v1 import (
    V119VCpoLimitDisciplineSupportDiscoveryAnalyzer,
)
from a_share_quant.strategy.v119w_cpo_limit_discipline_support_external_audit_v1 import (
    V119WCpoLimitDisciplineSupportExternalAuditAnalyzer,
)


def test_v119w_limit_discipline_external_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V119WCpoLimitDisciplineSupportExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119v_payload=V119VCpoLimitDisciplineSupportDiscoveryAnalyzer(repo_root=repo_root).analyze().as_dict(),
        v119m_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    assert result.summary["candidate_discriminator_name"] == "limit_discipline_support_score_candidate"
    assert result.summary["best_balanced_accuracy"] >= 0.0
