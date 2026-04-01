from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113s_cpo_training_start_readiness_review_v1 import (
    V113SCPOTrainingStartReadinessReviewAnalyzer,
    load_json_report,
    write_v113s_cpo_training_start_readiness_review_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113SCPOTrainingStartReadinessReviewAnalyzer()
    result = analyzer.analyze(
        v113q_payload=load_json_report(repo_root / "reports" / "analysis" / "v113q_cpo_training_material_readiness_audit_v1.json"),
        v113r_payload=load_json_report(repo_root / "reports" / "analysis" / "v113r_cpo_full_board_daily_bar_proxy_completion_v1.json"),
    )
    output_path = write_v113s_cpo_training_start_readiness_review_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113s_cpo_training_start_readiness_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
