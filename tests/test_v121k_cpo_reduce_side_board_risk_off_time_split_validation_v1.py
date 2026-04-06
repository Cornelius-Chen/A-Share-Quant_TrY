from pathlib import Path
import json

from a_share_quant.strategy.v121k_cpo_reduce_side_board_risk_off_time_split_validation_v1 import (
    V121KCpoReduceSideBoardRiskOffTimeSplitValidationAnalyzer,
)


def test_v121k_reduce_side_board_risk_off_time_split_validation_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121KCpoReduceSideBoardRiskOffTimeSplitValidationAnalyzer(repo_root=repo_root)
    payload = json.loads(
        (
            repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json"
        ).read_text(encoding="utf-8")
    )
    result = analyzer.analyze(v121j_payload=payload)
    assert result.summary["split_count"] == 3
    assert result.summary["mean_test_balanced_accuracy"] >= 0.0
