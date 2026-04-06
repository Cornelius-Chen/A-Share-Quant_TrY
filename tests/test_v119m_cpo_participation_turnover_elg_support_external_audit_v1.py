import json
from pathlib import Path

from a_share_quant.strategy.v119m_cpo_participation_turnover_elg_support_external_audit_v1 import main


def test_v119m_report_written() -> None:
    main()
    payload = json.loads(
        Path("reports/analysis/v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["best_balanced_accuracy"] >= 0.9
    assert payload["summary"]["external_pool_signal_clear"] is True
