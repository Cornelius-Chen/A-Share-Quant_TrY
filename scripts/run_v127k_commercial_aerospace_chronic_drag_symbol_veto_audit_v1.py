from pathlib import Path

from a_share_quant.strategy.v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1 import (
    V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
