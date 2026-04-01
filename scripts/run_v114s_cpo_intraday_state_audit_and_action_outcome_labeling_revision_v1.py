from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_v1 import (
    V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer,
    write_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
