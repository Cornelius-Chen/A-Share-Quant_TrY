from pathlib import Path

from a_share_quant.strategy.v134cv_commercial_aerospace_reduce_final_status_card_v1 import (
    V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134cw_commercial_aerospace_cv_reduce_do_not_drift_triage_v1 import (
    V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cv_commercial_aerospace_reduce_final_status_card_v1",
        result=status,
    )
    result = V134CWCommercialAerospaceCVReduceDoNotDriftTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cw_commercial_aerospace_cv_reduce_do_not_drift_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
