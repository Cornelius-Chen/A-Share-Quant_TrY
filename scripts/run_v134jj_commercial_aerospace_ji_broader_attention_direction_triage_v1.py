from pathlib import Path

from a_share_quant.strategy.v134jj_commercial_aerospace_ji_broader_attention_direction_triage_v1 import (
    V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jj_commercial_aerospace_ji_broader_attention_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
