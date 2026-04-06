from pathlib import Path

from a_share_quant.strategy.v125n_commercial_aerospace_structural_regime_discovery_v1 import (
    V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125n_commercial_aerospace_structural_regime_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
