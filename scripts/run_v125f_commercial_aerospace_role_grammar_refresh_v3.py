from pathlib import Path

from a_share_quant.strategy.v125f_commercial_aerospace_role_grammar_refresh_v3 import (
    V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125f_commercial_aerospace_role_grammar_refresh_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
