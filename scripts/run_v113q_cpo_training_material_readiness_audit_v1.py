from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113q_cpo_training_material_readiness_audit_v1 import (
    V113QCPOTrainingMaterialReadinessAuditAnalyzer,
    load_json_report,
    write_v113q_cpo_training_material_readiness_audit_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113QCPOTrainingMaterialReadinessAuditAnalyzer()
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113p_payload=load_json_report(repo_root / "reports" / "analysis" / "v113p_cpo_full_board_coverage_and_t1_audit_v1.json"),
    )
    output_path = write_v113q_cpo_training_material_readiness_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113q_cpo_training_material_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
