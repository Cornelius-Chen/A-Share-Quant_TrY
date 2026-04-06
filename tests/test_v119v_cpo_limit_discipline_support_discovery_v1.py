from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v119v_cpo_limit_discipline_support_discovery_v1 import (
    V119VCpoLimitDisciplineSupportDiscoveryAnalyzer,
)


def test_v119v_limit_discipline_support_discovery_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V119VCpoLimitDisciplineSupportDiscoveryAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["row_count"] > 0
    assert result.summary["candidate_discriminator_name"] == "limit_discipline_support_score_candidate"
    assert len(result.candidate_score_rows) == result.summary["row_count"]
