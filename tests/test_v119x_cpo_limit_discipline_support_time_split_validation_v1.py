from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v119v_cpo_limit_discipline_support_discovery_v1 import (
    V119VCpoLimitDisciplineSupportDiscoveryAnalyzer,
)
from a_share_quant.strategy.v119x_cpo_limit_discipline_support_time_split_validation_v1 import (
    V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer,
)


def test_v119x_limit_discipline_time_split_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119v_payload=V119VCpoLimitDisciplineSupportDiscoveryAnalyzer(repo_root=repo_root).analyze().as_dict(),
        v119n_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119n_cpo_participation_turnover_elg_support_time_split_validation_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    assert result.summary["split_count"] == 3
    assert len(result.split_rows) == 3
