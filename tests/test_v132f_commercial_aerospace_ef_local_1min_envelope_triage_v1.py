from pathlib import Path

from a_share_quant.strategy.v132f_commercial_aerospace_ef_local_1min_envelope_triage_v1 import (
    V132FCommercialAerospaceEFLocal1MinEnvelopeTriageAnalyzer,
)


def test_v132f_local_1min_envelope_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132FCommercialAerospaceEFLocal1MinEnvelopeTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_local_1min_pattern_envelopes_and_shift_next_to_rule_candidate_extraction"
    )
    assert result.summary["session_count"] == 6
