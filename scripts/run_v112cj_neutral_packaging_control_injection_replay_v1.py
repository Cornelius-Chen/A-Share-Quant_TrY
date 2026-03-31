from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cj_neutral_packaging_control_injection_replay_v1 import (
    V112CJNeutralPackagingControlInjectionReplayAnalyzer,
    load_json_report,
    write_v112cj_neutral_packaging_control_injection_replay_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cj_neutral_packaging_control_injection_replay_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CJNeutralPackagingControlInjectionReplayAnalyzer()
    result = analyzer.analyze(
        neutral_payload=load_json_report(repo_root / config["neutral_report_path"]),
        bp_payload=load_json_report(repo_root / config["bp_report_path"]),
        bz_payload=load_json_report(repo_root / config["bz_report_path"]),
        cf_payload=load_json_report(repo_root / config["cf_report_path"]),
        ch_payload=load_json_report(repo_root / config["ch_report_path"]),
    )
    output_path = write_v112cj_neutral_packaging_control_injection_replay_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CJ neutral packaging control injection replay report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
