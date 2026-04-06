from pathlib import Path
import json

from a_share_quant.strategy.v121f_cpo_close_context_time_split_audit_v1 import (
    V121FCpoCloseContextTimeSplitAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121FCpoCloseContextTimeSplitAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121e_cpo_close_context_narrowing_audit_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121e_payload=payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121f_cpo_close_context_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

