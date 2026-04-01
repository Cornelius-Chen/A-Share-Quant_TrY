from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cv_controlled_packaging_admission_extension_replay_v1 import (
    V112CVControlledPackagingAdmissionExtensionReplayAnalyzer,
    load_json_report,
    write_v112cv_controlled_packaging_admission_extension_replay_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cv_controlled_packaging_admission_extension_replay_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CVControlledPackagingAdmissionExtensionReplayAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / config["bh_report_path"]),
        ct_payload=load_json_report(repo_root / config["ct_report_path"]),
        cu_payload=load_json_report(repo_root / config["cu_report_path"]),
    )
    output_path = write_v112cv_controlled_packaging_admission_extension_replay_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CV controlled packaging admission extension replay report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
