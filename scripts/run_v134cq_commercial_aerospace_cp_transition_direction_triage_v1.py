from pathlib import Path

from a_share_quant.strategy.v134cp_commercial_aerospace_reduce_to_intraday_add_transition_protocol_v1 import (
    V134CPCommercialAerospaceReduceToIntradayAddTransitionProtocolV1Analyzer,
    write_report as write_protocol_report,
)
from a_share_quant.strategy.v134cq_commercial_aerospace_cp_transition_direction_triage_v1 import (
    V134CQCommercialAerospaceCPTransitionDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    protocol = V134CPCommercialAerospaceReduceToIntradayAddTransitionProtocolV1Analyzer(repo_root).analyze()
    write_protocol_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cp_commercial_aerospace_reduce_to_intraday_add_transition_protocol_v1",
        result=protocol,
    )
    result = V134CQCommercialAerospaceCPTransitionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cq_commercial_aerospace_cp_transition_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
