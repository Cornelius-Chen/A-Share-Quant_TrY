from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v119y_cpo_vwx_three_run_adversarial_triage_v1 import (
    V119YCpoVwxThreeRunAdversarialTriageAnalyzer,
)
from a_share_quant.strategy.v119v_cpo_limit_discipline_support_discovery_v1 import (
    V119VCpoLimitDisciplineSupportDiscoveryAnalyzer,
)
from a_share_quant.strategy.v119w_cpo_limit_discipline_support_external_audit_v1 import (
    V119WCpoLimitDisciplineSupportExternalAuditAnalyzer,
)
from a_share_quant.strategy.v119x_cpo_limit_discipline_support_time_split_validation_v1 import (
    V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer,
)


def test_v119y_vwx_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    v119v_payload = V119VCpoLimitDisciplineSupportDiscoveryAnalyzer(repo_root=repo_root).analyze().as_dict()
    v119w_payload = V119WCpoLimitDisciplineSupportExternalAuditAnalyzer(repo_root=repo_root).analyze(
        v119v_payload=v119v_payload,
        v119m_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    ).as_dict()
    v119x_payload = V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer(repo_root=repo_root).analyze(
        v119v_payload=v119v_payload,
        v119n_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119n_cpo_participation_turnover_elg_support_time_split_validation_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    ).as_dict()
    result = V119YCpoVwxThreeRunAdversarialTriageAnalyzer(repo_root=repo_root).analyze(
        v119v_payload=v119v_payload,
        v119w_payload=v119w_payload,
        v119x_payload=v119x_payload,
    )
    assert result.summary["branch_status"] == "explanatory_only"
    assert len(result.triage_rows) == 4
