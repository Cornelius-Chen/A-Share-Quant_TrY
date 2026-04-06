from pathlib import Path

from a_share_quant.strategy.v125g_commercial_aerospace_clean_boundary_control_surface_refresh_v1 import (
    V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125g_commercial_aerospace_clean_boundary_control_surface_refresh_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
