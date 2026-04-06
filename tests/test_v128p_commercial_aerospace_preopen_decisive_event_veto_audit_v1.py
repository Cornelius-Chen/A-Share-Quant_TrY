from pathlib import Path

from a_share_quant.strategy.v128p_commercial_aerospace_preopen_decisive_event_veto_audit_v1 import (
    V128PCommercialAerospacePreopenDecisiveEventVetoAuditAnalyzer,
)


def test_v128p_commercial_aerospace_preopen_decisive_event_veto_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128PCommercialAerospacePreopenDecisiveEventVetoAuditAnalyzer(repo_root).analyze()

    assert result.summary["reference_variant"] == "tail_weakdrift_full"
    assert int(result.summary["preopen_veto_trigger_day_count"]) == 0
    assert float(result.summary["veto_replay_final_equity"]) == float(result.summary["reference_final_equity"])
