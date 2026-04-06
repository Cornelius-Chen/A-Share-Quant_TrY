from pathlib import Path

from a_share_quant.strategy.v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1 import (
    V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
