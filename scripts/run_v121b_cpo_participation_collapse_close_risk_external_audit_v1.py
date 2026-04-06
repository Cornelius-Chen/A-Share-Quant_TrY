from pathlib import Path
import json

from a_share_quant.strategy.v121b_cpo_participation_collapse_close_risk_external_audit_v1 import (
    V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121a_cpo_participation_collapse_close_risk_discovery_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121a_payload=payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121b_cpo_participation_collapse_close_risk_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

