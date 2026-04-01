from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113u_cpo_execution_main_feed_readiness_audit_v1 import (
    V113UCPOExecutionMainFeedReadinessAuditAnalyzer,
    load_json_report,
    write_v113u_cpo_execution_main_feed_readiness_audit_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113UCPOExecutionMainFeedReadinessAuditAnalyzer()
    result = analyzer.analyze(
        repo_root=repo_root,
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v113t_payload=load_json_report(repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json"),
        v113q_payload=load_json_report(repo_root / "reports" / "analysis" / "v113q_cpo_training_material_readiness_audit_v1.json"),
    )
    output_path = write_v113u_cpo_execution_main_feed_readiness_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113u_cpo_execution_main_feed_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
