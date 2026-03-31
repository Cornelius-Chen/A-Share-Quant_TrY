from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cr_high_beta_core_derisk_replay_split_v1 import (
    V112CRHighBetaCoreDeriskReplaySplitAnalyzer,
    load_json_report,
    write_v112cr_high_beta_core_derisk_replay_split_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cr_high_beta_core_derisk_replay_split_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CRHighBetaCoreDeriskReplaySplitAnalyzer()
    result = analyzer.analyze(
        bh_payload=load_json_report(repo_root / config["bh_report_path"]),
        cq_payload=load_json_report(repo_root / config["cq_report_path"]),
    )
    output_path = write_v112cr_high_beta_core_derisk_replay_split_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CR high-beta core de-risk replay split report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
