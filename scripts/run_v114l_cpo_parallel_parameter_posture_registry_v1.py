from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114l_cpo_parallel_parameter_posture_registry_v1 import (
    V114LCpoParallelParameterPostureRegistryAnalyzer,
    write_v114l_cpo_parallel_parameter_posture_registry_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114LCpoParallelParameterPostureRegistryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114d_payload=load_json_report(repo_root / "reports" / "analysis" / "v114d_cpo_stable_zone_replay_injection_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114k_payload=load_json_report(repo_root / "reports" / "analysis" / "v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1.json"),
    )
    output_path = write_v114l_cpo_parallel_parameter_posture_registry_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114l_cpo_parallel_parameter_posture_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
